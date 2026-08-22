from .models import ParentMessage

def unread_messages_count(request):
    if request.user.is_authenticated and hasattr(request.user, "is_parent") and request.user.is_parent:
        count = ParentMessage.objects.filter(parent=request.user, is_read=False).count()
        return {"unread_messages_count": count}
    return {"unread_messages_count": 0}
