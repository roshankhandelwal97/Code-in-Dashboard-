from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from .models import Dashboard, Block, FileUpload, CodeBlock
from django.core.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializers import DashboardSerializer, BlockSerializer, FileUploadSerializer
import io
import sys
import pandas as pd
from contextlib import redirect_stdout, redirect_stderr
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import openai
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class DashboardListCreateView(generics.ListCreateAPIView):
    """
    GET: List all dashboards owned by the authenticated user
    POST: Create a new dashboard for the authenticated user
    """
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dashboard.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class DashboardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a single dashboard
    PUT/PATCH: Update a dashboard
    DELETE: Delete a dashboard
    """
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dashboard.objects.filter(owner=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this dashboard.")
        return obj


class BlockListCreateView(generics.ListCreateAPIView):
    """
    GET: List blocks for a given dashboard
    POST: Create a new block under a given dashboard
    """
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        dashboard_id = self.kwargs.get('dashboard_id')
        return Block.objects.filter(dashboard__id=dashboard_id, dashboard__owner=self.request.user)

    def perform_create(self, serializer):
        dashboard_id = self.kwargs.get('dashboard_id')
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id, owner=self.request.user)
        except Dashboard.DoesNotExist:
            raise PermissionDenied("Invalid dashboard or permission denied.")

        serializer.save(dashboard=dashboard)


class BlockRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a single block
    PUT/PATCH: Update a block
    DELETE: Delete a block
    """
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Block.objects.filter(dashboard__owner=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.dashboard.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this block.")
        return obj


class FileUploadView(generics.CreateAPIView):
    """
    POST /api/dashboard/<int:dashboard_id>/upload/
    """
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser, FormParser]  # needed for file uploads

    def post(self, request, *args, **kwargs):
        dashboard_id = self.kwargs.get('dashboard_id')
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id, owner=request.user)
        except Dashboard.DoesNotExist:
            raise PermissionDenied("You do not have permission for this dashboard.")

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.lower().endswith('.csv'):
            return Response({"detail": "Only CSV files are allowed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Optionally, you can add file size checks here
        # e.g., if file_obj.size > MAX_SIZE: raise some error

        # Create the FileUpload instance
        file_upload = FileUpload(dashboard=dashboard, file=file_obj)
        file_upload.save()

        serializer = self.get_serializer(file_upload)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CodeExecutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, block_id, *args, **kwargs):
        """
        POST /api/dashboard/blocks/<block_id>/run/
        Executes the code in the CodeBlock, loads CSV(s) from the same dashboard, and captures output.
        """
        # 1. Get the block and ensure user is the owner
        try:
            block = Block.objects.select_related('dashboard').get(id=block_id, dashboard__owner=request.user)
        except Block.DoesNotExist:
            return Response({"detail": "Block not found or permission denied."}, status=404)

        if block.block_type != Block.CODE:
            return Response({"detail": "This block is not a code block."}, status=400)

        # 2. Load the associated CSV files
        dashboard = block.dashboard
        csv_files = dashboard.files.all()  # All FileUpload objects

        dataframes = {}
        for file_upload in csv_files:
            if file_upload.file.name.lower().endswith('.csv'):
                try:
                    df = pd.read_csv(file_upload.file.path)
                    # You could store dataframes in a dict with the file name as the key
                    file_name = file_upload.file.name.split('/')[-1]  # or a unique base name
                    dataframes[file_name] = df
                except Exception as e:
                    return Response({"detail": f"Error loading CSV: {e}"}, status=400)

        # 3. Prepare the execution environment
        codeblock = CodeBlock.objects.get(block=block)
        code_to_run = codeblock.code

        # We'll define a local namespace, so the user can reference dataframes
        # Example usage in code: dataframes['my_data.csv']
        local_env = {
            'pd': pd,
            'dataframes': dataframes
        }

        # 4. Capture stdout/stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                exec(code_to_run, {}, local_env)
            except Exception as e:
                error_msg = f"{stderr_buffer.getvalue()}\nException: {e}"
                codeblock.output = error_msg
                codeblock.save()
                return Response({"output": error_msg}, status=400)

        # 5. Save the output in CodeBlock.output
        output = stdout_buffer.getvalue() or stderr_buffer.getvalue()
        codeblock.output = output
        codeblock.save()

        # 6. Return the updated block
        serializer = BlockSerializer(block)
        return Response(serializer.data, status=200)

class CodeGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, block_id, *args, **kwargs):
        """
        POST /api/dashboard/blocks/<block_id>/generate_code/
        Body: { "prompt": "some user prompt" }

        Steps:
        1. Retrieve the block & dashboard.
        2. Gather CSV schema (e.g., columns) from all CSVs in that dashboard.
        3. Call OpenAI (ChatGPT) with the user prompt + CSV schema.
        4. Update the CodeBlock.code with the generated snippet.
        5. Return the updated Block data.
        """

        # 1. Validate block & ownership
        try:
            block = Block.objects.select_related("dashboard").get(
                id=block_id, dashboard__owner=request.user
            )
        except Block.DoesNotExist:
            return Response(
                {"detail": "Block not found or permission denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        if block.block_type != Block.CODE:
            return Response(
                {"detail": "Not a code block."},
                status=status.HTTP_400_BAD_REQUEST
            )

        codeblock = CodeBlock.objects.get(block=block)

        # 2. Gather CSV schema from associated files
        dashboard = block.dashboard
        file_uploads = dashboard.files.all()

        csv_schemas = []

        for f in file_uploads:
            if f.file.name.lower().endswith(".csv"):
                try:
                    df = pd.read_csv(f.file.path, nrows=0)  # read only columns
                    columns = df.columns.tolist()
                    csv_schemas.append({
                        "filename": f.file.name.split("/")[-1],
                        "columns": columns
                    })
                except Exception:
                    # If a file is corrupted or unreadable, skip or log the error
                    pass

        # Construct a short text describing each CSV's columns
        schema_text_parts = [
            f"File: {schema['filename']}, Columns: {', '.join(schema['columns'])}"
            for schema in csv_schemas
        ]
        schema_text = "\n".join(schema_text_parts)
        
        existing_code = codeblock.code or ""


        # 3. Read the user prompt
        user_prompt = request.data.get("prompt", "")
        if not user_prompt:
            return Response(
                {"detail": "Prompt is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Prepare the full prompt for ChatGPT
        # You can adjust this prompt to suit your style or desired constraints
        full_prompt = f"""
        You are a code generation assistant. The CSV files are already loaded in memory 
        as Pandas DataFrames, accessible via a Python dictionary called 'dataframes'. 

        **IMPORTANT:**
        - Do NOT include 'import pandas as pd'.
        - Do NOT read files from disk (e.g., 'pd.read_csv').
        - Do NOT use code fences or markdown formatting.
        - DO NOT just create the dataframes, give code such that the output is printed
        - If there's existing code, refine or extend it based on the user request

        Existing code (may be empty if none yet):
        {existing_code}


        The user has these CSV schemas:
        {schema_text}

        User request:
        {user_prompt}

        Return ONLY the code, nothing else.
        """

        # 5. Call the OpenAI API (ChatGPT)
        openai.api_key = settings.OPENAI_API_KEY

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant specialized in generating "
                            "pandas-based Python code. Only provide the code as an answer."
                        )
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=200,
                temperature=0.5,
                stop=["```"] 
            )
            generated_code = response.choices[0].message.content.strip()
        except Exception as e:
            return Response(
                {"detail": f"OpenAI API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 6. Update the CodeBlock with the generated code
        codeblock.code = generated_code
        codeblock.save()

        # 7. Return the updated block data
        block_serializer = BlockSerializer(block)
        return Response(block_serializer.data, status=status.HTTP_200_OK)

        