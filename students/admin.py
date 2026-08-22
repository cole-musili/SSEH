from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "student_id", "stream", "grade", "parent_full_name", "status")
    search_fields = (
        "user__first_name", 
        "user__last_name", 
        "student_id", 
        "stream__code", 
        "stream__grade__name"
    )
    list_filter = ("stream__grade", "stream__year", "status")
    autocomplete_fields = ("stream", "parent")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "parent", "stream")
