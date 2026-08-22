from django.contrib import admin
from .models import TeacherRecord, Timetable, SchoolAdminProfile
from teachers.models import TeacherProfile 


# 🧑‍🏫 Teacher Record Admin
@admin.register(TeacherRecord)
class TeacherRecordAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialization", "phone", "employment_date", "status")
    list_filter = ("status", "specialization")
    search_fields = ("full_name", "specialization__name", "phone")
    filter_horizontal = ("assigned_streams",)

    fieldsets = (
        ("Personal Information", {
            "fields": ("full_name", "gender", "phone", "email", "photo")
        }),
        ("Professional Details", {
            "fields": ("qualification", "specialization", "assigned_streams", "employment_date", "status")
        }),
    )


# 🗓️ Timetable Admin
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("stream", "day_of_week", "subject", "display_teacher", "start_time", "end_time")
    list_filter = ("day_of_week", "stream", "subject")
    search_fields = (
        "stream__grade__name",
        "stream__code",
        "subject__name",
        "teacher_record__full_name",
        "teacher_name",
    )

    def display_teacher(self, obj):
        return obj.display_teacher  # uses helper property from model

    display_teacher.short_description = "Teacher"


# 🏫 School Admin Profile Admin
@admin.register(SchoolAdminProfile)
class SchoolAdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "status")
    list_filter = ("status",)
    search_fields = ("user__username", "full_name", "phone")

    fieldsets = (
        (None, {
            "fields": ("user", "full_name", "phone", "photo", "status")
        }),
    )

