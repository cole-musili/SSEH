from django.contrib import admin
from .models import Message, ParentMessage


class ParentMessageInline(admin.TabularInline):
    model = ParentMessage
    extra = 0
    fields = ("parent", "is_read", "read_at")
    readonly_fields = ("read_at",)
    can_delete = False
    show_change_link = True


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("title", "scope", "sender", "target_display", "created_at")
    list_filter = ("scope", "created_at", "sender__is_teacher")
    search_fields = ("title", "body", "sender__username")
    date_hierarchy = "created_at"
    inlines = [ParentMessageInline]

    def target_display(self, obj):
        """Show who the message is targeted to."""
        if obj.scope == "stream" and obj.stream:
            return f"Stream: {obj.stream}"
        elif obj.scope == "student" and obj.student:
            return f"Student: {obj.student.user.username}"
        elif obj.scope == "subject" and obj.subject:
            return f"Subject: {obj.subject.name}"
        return "General"
    target_display.short_description = "Target"


@admin.register(ParentMessage)
class ParentMessageAdmin(admin.ModelAdmin):
    list_display = ("parent", "message_title", "is_read", "read_at")
    list_filter = ("is_read", "message__scope")
    search_fields = ("message__title", "parent__username")
    readonly_fields = ("read_at",)

    def message_title(self, obj):
        return obj.message.title
    message_title.short_description = "Message"
