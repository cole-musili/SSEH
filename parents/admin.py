from django.contrib import admin
from .models import ParentProfile

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "linked_students", "status")
    list_filter = ("status",)
    search_fields = (
        "user__username",
        "user__email",
        "students__user__username",
        "students__student_id",
    )
    filter_horizontal = ("students",)  # adds the nice dual list selector for M2M

    def linked_students(self, obj):
        """Display all students linked to this parent."""
        students = obj.students.all()
        if students:
            return ", ".join([s.user.username for s in students])
        return "—"
    linked_students.short_description = "Linked Students"
