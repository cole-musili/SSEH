from django.contrib import admin
from .models import TeacherProfile, TeacherQuiz


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "teacher_id", "assigned_quizzes_count", "status")
    list_filter = ("status",)
    search_fields = ("user__first_name", "user__last_name", "user__username", "teacher_id")


    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    full_name.short_description = "Full Name"

    def username(self, obj):
        return obj.user.username

    def assigned_quizzes_count(self, obj):
        return obj.user.teacher_quizzes.count()
    assigned_quizzes_count.short_description = "Quizzes Assigned"


@admin.register(TeacherQuiz)
class TeacherQuizAdmin(admin.ModelAdmin):
    list_display = ("quiz", "teacher_full_name", "stream", "created_at")
    list_filter = ("stream__year", "stream__grade")
    search_fields = ("quiz__title", "teacher__first_name", "teacher__last_name", "stream__code", "stream__grade__name")
    autocomplete_fields = ("teacher", "quiz", "stream")

    def teacher_full_name(self, obj):
        """Show teacher’s full name in admin list."""
        if obj.teacher.first_name or obj.teacher.last_name:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip()
        return obj.teacher.username
    teacher_full_name.short_description = "Teacher"

