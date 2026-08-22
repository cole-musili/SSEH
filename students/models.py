# students/models.py

from django.db import models
from django.conf import settings
from quizzes.models import Quiz, Question

User = settings.AUTH_USER_MODEL

class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, null=True, unique=True)

    # Link to parent user
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        limit_choices_to={'is_parent': True}
    )

    stream = models.ForeignKey(
        'school.Stream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    grade = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True, default='default-avatar.png')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def full_name(self):
        """Return student's full name."""
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username  # fallback

    def parent_full_name(self):
        """Return parent’s full name if available."""
        if self.parent:
            if self.parent.first_name or self.parent.last_name:
                return f"{self.parent.first_name} {self.parent.last_name}".strip()
            return self.parent.username
        return "-"

    def __str__(self):
        return f"{self.full_name()} ({self.student_id or 'No ID'})"

class QuizResult(models.Model):
    """Stores quiz results for a student."""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name="results"
    )
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name="results"
    )
    score = models.IntegerField(default=0)
    taken_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Only approved results visible to parents

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title} ({self.score})"


class Answer(models.Model):
    """Individual answers for a quiz result."""
    result = models.ForeignKey(
        QuizResult, 
        on_delete=models.CASCADE, 
        related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # 'A', 'B', 'C', 'D'
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.result.student.user.username} - {self.question.text[:20]}"
