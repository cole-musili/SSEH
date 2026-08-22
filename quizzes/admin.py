from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("text", "option_a", "option_b", "option_c", "option_d", "correct_answer")
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "question_count", "created_at", "updated_at")
    search_fields = ("title", "description", "created_by__username")
    list_filter = ("created_at",)
    autocomplete_fields = ("created_by",)
    inlines = [QuestionInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
