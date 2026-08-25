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
    filter_horizontal = ("students",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("students__user")

    def linked_students(self, obj):
        students = obj.students.all()
        if students:
            return ", ".join([s.user.username for s in students])
        return "—"
    linked_students.short_description = "Linked Students"