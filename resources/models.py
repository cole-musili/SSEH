from django.db import models
from django.conf import settings
import os

User = settings.AUTH_USER_MODEL


def get_upload_path(instance, filename):
    """Organize uploads by uploader."""
    return f"resources/{instance.uploader.username}/{filename}"


class Resource(models.Model):
    VISIBILITY_CHOICES = [
        ("all", "Everyone"),
        ("students", "Students Only"),
        ("teachers", "Teachers Only"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=get_upload_path)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_resources")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="all")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.uploader})"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower().replace(".", "")

    def icon(self):
        """Return emoji or icon name for file type."""
        ext = self.file_extension
        if ext in ["pdf"]:
            return "📕"
        elif ext in ["doc", "docx"]:
            return "📘"
        elif ext in ["xls", "xlsx", "csv"]:
            return "📊"
        elif ext in ["ppt", "pptx"]:
            return "📑"
        elif ext in ["zip", "rar"]:
            return "📦"
        elif ext in ["mp4", "mov", "avi"]:
            return "🎬"
        elif ext in ["jpg", "png", "jpeg"]:
            return "🖼️"
        else:
            return "📄"


