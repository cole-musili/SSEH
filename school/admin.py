from django.contrib import admin
from .models import (
    School, AcademicYear, Term, GradeLevel, Stream,
    Subject, Enrollment, TeacherAssignment
)


# ---------- Custom Admin Actions ----------
@admin.action(description="Set selected Academic Year as current")
def make_current_year(modeladmin, request, queryset):
    # Only one year can be current
    AcademicYear.objects.update(is_current=False)
    queryset.update(is_current=True)


# ---------- AcademicYear ----------
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_current")
    list_editable = ("is_current",)
    ordering = ("-start_date",)
    actions = [make_current_year]
    search_fields = ("name",)
    list_filter = ("is_current",)


# ---------- Term ----------
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "start_date", "end_date")
    list_filter = ("year",)
    search_fields = ("name", "year__name")
    ordering = ("year__start_date", "start_date")


# ---------- GradeLevel ----------
@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)
    search_fields = ("name",)


# ---------- Stream ----------
@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("grade", "code", "year", "homeroom_teacher")
    list_filter = ("year", "grade")
    search_fields = ("grade__name", "code", "homeroom_teacher__username")
    ordering = ("grade__order", "code")
    autocomplete_fields = ("homeroom_teacher",)


# ---------- Subject ----------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code")
    search_fields = ("name", "short_code")


# ---------- Enrollment ----------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "stream", "year", "date_enrolled")
    list_filter = ("year", "stream__grade")
    search_fields = ("student__user__username", "stream__code")
    autocomplete_fields = ("student", "stream", "year")


# ---------- TeacherAssignment ----------
@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "stream", "term")
    list_filter = ("term__year", "stream__grade", "subject")
    search_fields = (
        "teacher__username",
        "subject__name",
        "stream__code",
        "term__name",
    )
    autocomplete_fields = ("teacher", "subject", "stream", "term")
    ordering = ("stream__grade__order", "subject__name")

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email")
    ordering = ("name",)