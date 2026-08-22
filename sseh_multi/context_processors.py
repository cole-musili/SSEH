from support.models import ContactMessage

def unread_messages_count(request):
    if request.user.is_authenticated and getattr(request.user, "is_school_admin", False):
        count = ContactMessage.objects.filter(is_replied=False).count()
    else:
        count = 0
    return {"unread_message_count": count}
