from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    replied_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_replies"
    )
    # New fields
    reply_text = models.TextField(blank=True, null=True)
    replied_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="replied_messages")
    replied_at = models.DateTimeField(null=True, blank=True)

    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} from {self.name}"

