from django.db import models
from accounts.models import User
from students.models import StudentProfile

class ParentProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(
        StudentProfile,
        related_name="parents",
        blank=True,
    )

    # Add personal details
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='parent_photos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        """Display parent's full name or fallback to user info"""
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        if not name:
            name = self.user.get_full_name() or self.user.username
        count = self.students.count()
        return f"{name} (linked to {count} student{'s' if count != 1 else ''})"

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.user.get_full_name()

