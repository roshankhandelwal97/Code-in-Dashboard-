# dashboard_app/serializers.py
from rest_framework import serializers
from .models import Dashboard, Block, TextBlock, CodeBlock
from .models import FileUpload

class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBlock
        fields = ['content']

class CodeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeBlock
        fields = ['language', 'code', 'output']

class BlockSerializer(serializers.ModelSerializer):
    textblock = TextBlockSerializer(required=False)
    codeblock = CodeBlockSerializer(required=False)

    class Meta:
        model = Block
        fields = [
            'id',
            'block_type',
            'position',
            'created_at',
            'updated_at',
            'textblock',
            'codeblock',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        We need to handle nested creation for TextBlock or CodeBlock.
        """
        block_type = validated_data.get('block_type')
        textblock_data = validated_data.pop('textblock', None)
        codeblock_data = validated_data.pop('codeblock', None)

        block = Block.objects.create(**validated_data)

        if block_type == Block.TEXT and textblock_data:
            TextBlock.objects.create(block=block, **textblock_data)
        elif block_type == Block.CODE and codeblock_data:
            CodeBlock.objects.create(block=block, **codeblock_data)

        return block

    def update(self, instance, validated_data):
        """
        Handle updates to the parent Block and the nested text/code block.
        """
        block_type = validated_data.get('block_type', instance.block_type)
        textblock_data = validated_data.pop('textblock', None)
        codeblock_data = validated_data.pop('codeblock', None)

        instance.block_type = block_type
        instance.position = validated_data.get('position', instance.position)
        instance.save()

        if block_type == Block.TEXT and textblock_data:
            if hasattr(instance, 'textblock'):
                for key, value in textblock_data.items():
                    setattr(instance.textblock, key, value)
                instance.textblock.save()
            else:
                TextBlock.objects.create(block=instance, **textblock_data)

            if hasattr(instance, 'codeblock'):
                instance.codeblock.delete()

        elif block_type == Block.CODE and codeblock_data:
            if hasattr(instance, 'codeblock'):
                for key, value in codeblock_data.items():
                    setattr(instance.codeblock, key, value)
                instance.codeblock.save()
            else:
                CodeBlock.objects.create(block=instance, **codeblock_data)

            if hasattr(instance, 'textblock'):
                instance.textblock.delete()

        return instance


class DashboardSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ['id', 'title', 'created_at', 'updated_at', 'blocks']
        read_only_fields = ['created_at', 'updated_at']

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
