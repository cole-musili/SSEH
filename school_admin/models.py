# school_admin/models.py
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from school.models import Stream, Subject


# ✅ School Admin Profile (linked to User)
class SchoolAdminProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_duty', 'On Duty'),
        ('away', 'Away'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='school_admin_profile'
    )
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='school_admins/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  # 🆕 Added

    def __str__(self):
        return self.full_name or self.user.username


# ✅ Teacher Record
class TeacherRecord(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teacher_record'
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    qualification = models.CharField(max_length=100, blank=True)
    specialization = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_streams = models.ManyToManyField(Stream, blank=True)
    employment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('leave', 'On Leave'), ('inactive', 'Inactive')],
        default='active'
    )
    photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.specialization})"


# ✅ Timetable
class Timetable(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="timetables")
    day_of_week = models.CharField(max_length=10, choices=[
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher_record = models.ForeignKey(
        "school_admin.TeacherRecord",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="timetable_entries"
    )
    teacher_name = models.CharField(max_length=120, blank=True)
    is_substitution = models.BooleanField(default=False)
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('stream', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        overlap = Timetable.objects.filter(
            stream=self.stream,
            day_of_week=self.day_of_week
        ).exclude(pk=self.pk).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists()
        if overlap:
            raise ValidationError("Another lesson overlaps this time slot.")
        if not self.teacher_record and not self.teacher_name:
            raise ValidationError("Provide a teacher record or teacher name.")

    @property
    def display_teacher(self):
        return self.teacher_record.full_name if self.teacher_record else self.teacher_name or "—"

    def __str__(self):
        return f"{self.stream} • {self.day_of_week} {self.start_time}-{self.end_time} • {self.subject}"


# ✅ Academic Year
class AcademicYear(models.Model):
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year_start']

    def __str__(self):
        return f"{self.year_start}/{self.year_end}"


# ✅ Term
class Term(models.Model):
    TERM_CHOICES = [('Term 1', 'Term 1'), ('Term 2', 'Term 2'), ('Term 3', 'Term 3')]
    name = models.CharField(max_length=50, choices=TERM_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['academic_year', 'start_date']

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    def save(self, *args, **kwargs):
        if self.is_current:
            Term.objects.filter(academic_year=self.academic_year).update(is_current=False)
        super().save(*args, **kwargs)
