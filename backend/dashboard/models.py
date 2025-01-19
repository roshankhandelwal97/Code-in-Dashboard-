from django.db import models
from django.conf import settings
import os

class Dashboard(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Block(models.Model):
    TEXT = 'text'
    CODE = 'code'
    BLOCK_TYPES = [(TEXT, 'Text'), (CODE, 'Code')]

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES, default=TEXT)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TextBlock(models.Model):
    block = models.OneToOneField(Block, on_delete=models.CASCADE, primary_key=True)
    content = models.TextField(blank=True)

class CodeBlock(models.Model):
    block = models.OneToOneField(Block, on_delete=models.CASCADE, primary_key=True)
    language = models.CharField(max_length=20, default='python')
    code = models.TextField(blank=True)
    output = models.TextField(blank=True)


def csv_upload_path(instance, filename):
    # Construct a path like: dashboard_<id>/filename.csv
    return f"dashboard_{instance.dashboard.id}/{filename}"

class FileUpload(models.Model):
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=csv_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.file.name)
