# communications/models.py

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Message(models.Model):
    """Main message entity teachers send to a stream, subject, or specific student."""

    SCOPE_CHOICES = [
        ('stream', 'Stream'),
        ('subject', 'Subject'),
        ('student', 'Student'),
    ]

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        limit_choices_to={'is_teacher': True}
    )
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)

    # 🩵 Lazy references prevent circular import during migration
    stream = models.ForeignKey('school.Stream', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey('school.Subject', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.stream or self.subject or self.student or "General"
        return f"{self.title} → {target}"


class ParentMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="deliveries")
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.message.title} → {self.parent.username}"
    

class MessageReply(models.Model):
    parent_message = models.ForeignKey(
        ParentMessage,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.body[:30]}"

    class Meta:
        ordering = ["created_at"]


