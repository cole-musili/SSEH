from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# -------------------------------
# 🏫 Multi-School Root Model
# -------------------------------
class School(models.Model):
    """Represents a specific school in the system."""
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -------------------------------
# 📅 Academic Structure
# -------------------------------
class AcademicYear(models.Model):
    """Defines an academic year (e.g., 2025/2026)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ("school", "name")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Term(models.Model):
    """Defines school terms/semesters within a year."""
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=20)  # Term 1, Term 2, etc.
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ("year", "name")
        ordering = ['year__start_date', 'start_date']

    def __str__(self):
        return f"{self.year.name} - {self.name}"


class GradeLevel(models.Model):
    """Defines the grade levels — e.g., Grade 7, Form 1, etc."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_levels")
    name = models.CharField(max_length=30)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("school", "name")
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Stream(models.Model):
    """
    Defines class streams, e.g., '7 North', '7 Green'.
    Each stream belongs to a grade and an academic year.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="streams")
    grade = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name="streams")
    code = models.CharField(max_length=30)  # "North", "Green", etc.
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="streams")
    homeroom_teacher = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"is_teacher": True},
        related_name="homerooms"
    )

    class Meta:
        unique_together = ("school", "grade", "code", "year")
        ordering = ["grade__order", "code"]

    def __str__(self):
        return f"{self.grade.name} {self.code} ({self.year.name})"


class Subject(models.Model):
    """Subjects like Math, English, etc."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=60)
    short_code = models.CharField(max_length=15)

    class Meta:
        unique_together = ("school", "name", "short_code")

    def __str__(self):
        return f"{self.name} ({self.school.name})"


# -------------------------------
# 🎓 Enrollment & Teaching
# -------------------------------
class Enrollment(models.Model):
    """
    Links students to streams for a specific academic year.
    One enrollment per student per academic year.
    """
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="enrollments")
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "year")

    def __str__(self):
        return f"{self.student.user.username} → {self.stream}"


class TeacherAssignment(models.Model):
    """
    Defines which teacher teaches which subject in which stream and term.
    """
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_teacher": True},
        related_name="assignments"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="subject_assignments")
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("teacher", "subject", "stream", "term")

    def __str__(self):
        return f"{self.teacher.username} → {self.subject.name} ({self.stream})"
