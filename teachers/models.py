from django.db import models
from django.conf import settings
from quizzes.models import Quiz

User = settings.AUTH_USER_MODEL


class TeacherProfile(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_duty', 'On Duty'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    ]
     
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def full_name(self):
        """Return teacher’s full name, fallback to username."""
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username

    def __str__(self):
        """Show username (technical reference)."""
        return self.user.username


class TeacherQuiz(models.Model):
    """Represents a quiz assigned by a teacher to a specific stream."""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='teacher_quizzes'
    )
    quiz = models.OneToOneField(
        Quiz,
        on_delete=models.CASCADE,
        related_name='teacher_quiz'
    )
    stream = models.ForeignKey(
        "school.Stream",
        on_delete=models.CASCADE,
        related_name="teacher_quizzes",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('teacher', 'quiz', 'stream')
        verbose_name_plural = 'Teacher Quizzes'

    def __str__(self):
        stream_name = self.stream.code if self.stream else "No Stream"
        return f"{self.quiz.title} → {stream_name} ({self.teacher.username})"
