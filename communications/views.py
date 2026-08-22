from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message, ParentMessage
from school.models import Stream, Subject
from students.models import StudentProfile
from accounts.models import User  # assuming your User model extends AbstractUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from communications.models import ParentMessage
from django.db.models import Q
from .models import ParentMessage, MessageReply


@login_required
def teacher_send_message(request):
    if not request.user.is_teacher:
        return redirect("accounts:dashboard_redirect")

    streams = Stream.objects.all()
    subjects = Subject.objects.all()
    students = StudentProfile.objects.all()

    if request.method == "POST":
        scope = request.POST.get("scope")
        title = request.POST.get("title")
        body = request.POST.get("body")

        message = Message.objects.create(
            sender=request.user,
            scope=scope,
            title=title,
            body=body,
        )

        delivered_to = 0  # for debugging feedback

        if scope == "stream":
            stream = Stream.objects.get(id=request.POST.get("stream"))
            message.stream = stream
            message.save()

            for student in stream.students.all():
                if student.parent:
                    ParentMessage.objects.create(message=message, parent=student.parent)
                    delivered_to += 1

        elif scope == "subject":
            subject = Subject.objects.get(id=request.POST.get("subject"))
            message.subject = subject
            message.save()

            qs = StudentProfile.objects.filter(
                stream__subject_assignments__subject=subject
            ).distinct()
            for student in qs:
                if student.parent:
                    ParentMessage.objects.create(message=message, parent=student.parent)
                    delivered_to += 1

        elif scope == "student":
            student = StudentProfile.objects.get(id=request.POST.get("student"))
            message.student = student
            message.save()
            if student.parent:
                ParentMessage.objects.create(message=message, parent=student.parent)
                delivered_to += 1

        messages.success(request, f"✅ Message sent to {delivered_to} parent(s).")
        return redirect("communications:teacher_message_list")

    return render(
        request,
        "communications/teacher_send_message.html",
        {"streams": streams, "subjects": subjects, "students": students},
    )

def get_unread_count(user):
    """Return count of unread messages for a parent"""
    if user.is_authenticated and hasattr(user, "is_parent") and user.is_parent:
        return ParentMessage.objects.filter(parent=user, is_read=False).count()
    return 0


@login_required
def teacher_message_list(request):
    """List messages sent by a teacher"""
    messages = Message.objects.filter(sender=request.user).order_by("-created_at")
    return render(request, "communications/teacher_message_list.html", {"messages": messages})


@login_required
def parent_inbox(request):
    if not request.user.is_parent:
        from django.contrib import messages
        messages.error(request, "Only parents can access this page.")
        return redirect("accounts:dashboard_redirect")

    # Find the child’s stream(s)
    children = request.user.parentprofile.children.all()
    streams = [child.stream for child in children if hasattr(child, 'stream') and child.stream]
    
    messages_qs = Message.objects.filter(stream__in=streams).select_related('sender', 'stream').order_by('-created_at')

    return render(request, "communications/parent_inbox.html", {"messages": messages_qs})

@login_required
def parent_message_list(request):
    """Parent inbox showing messages from teachers"""
    parent_messages = ParentMessage.objects.filter(
        parent=request.user
    ).select_related("message").order_by("-message__created_at")

    return render(
        request,
        "communications/parent_message_list.html",
        {"parent_messages": parent_messages},
    )

@login_required
def parent_message_detail(request, message_id):
    """Show a full message for the parent, and allow replying."""
    parent_message = get_object_or_404(
        ParentMessage,
        message_id=message_id,
        parent=request.user
    )

    # Mark as read if not already
    if not parent_message.is_read:
        parent_message.is_read = True
        parent_message.read_at = timezone.now()
        parent_message.save()

    # Handle reply submission
    if request.method == "POST":
        body = request.POST.get("reply")
        if body.strip():
            MessageReply.objects.create(
                parent_message=parent_message,
                sender=request.user,
                body=body
            )
            messages.success(request, "Reply sent successfully.")
            return redirect("communications:parent_message_detail", message_id=message_id)

    replies = parent_message.replies.select_related("sender").order_by("created_at")

    return render(request, "communications/parent_message_detail.html", {
        "parent_message": parent_message,
        "replies": replies,
    })

@login_required
def teacher_message_detail(request, pk):
    """Show a teacher's sent message and all replies from parents."""
    message = get_object_or_404(Message, pk=pk, sender=request.user)
    related_parents = ParentMessage.objects.filter(message=message).select_related("parent")

    # Flatten replies from all parent threads
    all_replies = MessageReply.objects.filter(parent_message__in=related_parents).select_related("sender")

    # Optional: allow teacher to reply back to a specific parent
    if request.method == "POST":
        parent_message_id = request.POST.get("parent_message_id")
        reply_text = request.POST.get("reply")
        if parent_message_id and reply_text.strip():
            parent_message = get_object_or_404(ParentMessage, id=parent_message_id)
            MessageReply.objects.create(
                parent_message=parent_message,
                sender=request.user,
                body=reply_text
            )
            messages.success(request, "Reply sent to parent.")
            return redirect("communications:teacher_message_detail", pk=pk)

    context = {
        "message": message,
        "related_parents": related_parents,
        "all_replies": all_replies,
    }
    return render(request, "communications/teacher_message_detail.html", context)



# 🧠 Student message inbox
@login_required
def student_message_list(request):
    """Show all messages for the logged-in student."""
    if not getattr(request.user, "is_student", False):
        return render(request, "403.html", status=403)

    student = request.user.studentprofile

    # Fetch messages for this student OR their stream
    messages_qs = Message.objects.filter(
        Q(scope="student", student=student) |
        Q(scope="stream", stream=student.stream)
    ).order_by("-created_at").distinct()

    return render(
        request,
        "communications/student_message_list.html",
        {"messages": messages_qs}
    )

@login_required
def student_message_detail(request, pk):
    """
    Display a message sent to this student or to their stream.
    """
    student = request.user.studentprofile

    # Allow messages either directly to this student OR to their stream
    message = get_object_or_404(
        Message,
        Q(pk=pk) & (
            Q(student=student) |
            Q(stream=student.stream)
        )
    )

    # Optionally mark message as read
    if hasattr(message, "is_read") and not message.is_read:
        message.is_read = True
        message.save(update_fields=["is_read"])

    return render(request, "communications/student_message_detail.html", {"message": message})