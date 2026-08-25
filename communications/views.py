from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Message, ParentMessage, MessageReply
from school.models import Stream, Subject
from students.models import StudentProfile


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

        delivered_to = 0

        # Send to entire stream
        if scope == "stream":
            stream = get_object_or_404(
                Stream,
                id=request.POST.get("stream")
            )

            message.stream = stream
            message.save(update_fields=["stream"])

            for student in stream.students.all():
                if student.parent:
                    ParentMessage.objects.create(
                        message=message,
                        parent=student.parent
                    )
                    delivered_to += 1

        # Send to students taking a subject
        elif scope == "subject":
            subject = get_object_or_404(
                Subject,
                id=request.POST.get("subject")
            )

            message.subject = subject
            message.save(update_fields=["subject"])

            students_qs = StudentProfile.objects.filter(
                stream__subject_assignments__subject=subject
            ).distinct()

            for student in students_qs:
                if student.parent:
                    ParentMessage.objects.create(
                        message=message,
                        parent=student.parent
                    )
                    delivered_to += 1

        # Send directly to one student
        elif scope == "student":
            student = get_object_or_404(
                StudentProfile,
                id=request.POST.get("student")
            )

            message.student = student
            message.save(update_fields=["student"])

            if student.parent:
                ParentMessage.objects.create(
                    message=message,
                    parent=student.parent
                )
                delivered_to += 1

        messages.success(
            request,
            f"✅ Message sent to {delivered_to} parent(s)."
        )

        return redirect("communications:teacher_message_list")

    return render(
        request,
        "communications/teacher_send_message.html",
        {
            "streams": streams,
            "subjects": subjects,
            "students": students,
        },
    )


def get_unread_count(user):
    """Return the number of unread messages for a parent."""

    if (
        user.is_authenticated
        and getattr(user, "is_parent", False)
    ):
        return ParentMessage.objects.filter(
            parent=user,
            is_read=False
        ).count()

    return 0


@login_required
def teacher_message_list(request):
    """List messages sent by the logged-in teacher."""

    teacher_messages = Message.objects.filter(
        sender=request.user
    ).order_by("-created_at")

    return render(
        request,
        "communications/teacher_message_list.html",
        {
            "messages": teacher_messages
        }
    )


@login_required
def parent_inbox(request):
    if not request.user.is_parent:
        messages.error(
            request,
            "Only parents can access this page."
        )
        return redirect("accounts:dashboard_redirect")

    children = request.user.parentprofile.children.all()

    streams = [
        child.stream
        for child in children
        if hasattr(child, "stream") and child.stream
    ]

    messages_qs = (
        Message.objects
        .filter(stream__in=streams)
        .select_related("sender", "stream")
        .order_by("-created_at")
    )

    return render(
        request,
        "communications/parent_inbox.html",
        {
            "messages": messages_qs
        }
    )


@login_required
def parent_message_list(request):
    """Parent inbox showing messages from teachers."""

    parent_messages = (
        ParentMessage.objects
        .filter(parent=request.user)
        .select_related("message")
        .order_by("-message__created_at")
    )

    return render(
        request,
        "communications/parent_message_list.html",
        {
            "parent_messages": parent_messages
        }
    )


@login_required
def parent_message_detail(request, message_id):
    """Show a full message to the parent and allow replying."""

    parent_message = get_object_or_404(
        ParentMessage,
        message_id=message_id,
        parent=request.user
    )

    # Mark message as read
    if not parent_message.is_read:
        parent_message.is_read = True
        parent_message.read_at = timezone.now()
        parent_message.save(
            update_fields=["is_read", "read_at"]
        )

    # Handle reply
    if request.method == "POST":
        body = request.POST.get("reply", "").strip()

        if body:
            MessageReply.objects.create(
                parent_message=parent_message,
                sender=request.user,
                body=body
            )

            messages.success(
                request,
                "Reply sent successfully."
            )

            return redirect(
                "communications:parent_message_detail",
                message_id=message_id
            )

    replies = (
        parent_message.replies
        .select_related("sender")
        .order_by("created_at")
    )

    return render(
        request,
        "communications/parent_message_detail.html",
        {
            "parent_message": parent_message,
            "replies": replies,
        }
    )


@login_required
def teacher_message_detail(request, pk):
    """Show a teacher's sent message and replies from parents."""

    message = get_object_or_404(
        Message,
        pk=pk,
        sender=request.user
    )

    related_parents = (
        ParentMessage.objects
        .filter(message=message)
        .select_related("parent")
    )

    all_replies = (
        MessageReply.objects
        .filter(parent_message__in=related_parents)
        .select_related("sender")
        .order_by("created_at")
    )

    # Allow teacher to reply to a specific parent
    if request.method == "POST":
        parent_message_id = request.POST.get(
            "parent_message_id"
        )

        reply_text = request.POST.get(
            "reply",
            ""
        ).strip()

        if parent_message_id and reply_text:
            parent_message = get_object_or_404(
                ParentMessage,
                id=parent_message_id,
                message=message
            )

            MessageReply.objects.create(
                parent_message=parent_message,
                sender=request.user,
                body=reply_text
            )

            messages.success(
                request,
                "Reply sent to parent."
            )

            return redirect(
                "communications:teacher_message_detail",
                pk=pk
            )

    context = {
        "message": message,
        "related_parents": related_parents,
        "all_replies": all_replies,
    }

    return render(
        request,
        "communications/teacher_message_detail.html",
        context
    )


@login_required
def student_message_list(request):
    """Show all messages for the logged-in student."""

    if not getattr(request.user, "is_student", False):
        return render(
            request,
            "403.html",
            status=403
        )

    student = request.user.studentprofile

    messages_qs = (
        Message.objects
        .filter(
            Q(scope="student", student=student)
            | Q(scope="stream", stream=student.stream)
        )
        .order_by("-created_at")
        .distinct()
    )

    return render(
        request,
        "communications/student_message_list.html",
        {
            "messages": messages_qs
        }
    )


@login_required
def student_message_detail(request, pk):
    """Display a message sent directly to this student or their stream."""

    student = request.user.studentprofile

    message = get_object_or_404(
        Message,
        Q(pk=pk)
        & (
            Q(student=student)
            | Q(stream=student.stream)
        )
    )

    if hasattr(message, "is_read") and not message.is_read:
        message.is_read = True
        message.save(update_fields=["is_read"])

    return render(
        request,
        "communications/student_message_detail.html",
        {
            "message": message
        }
    )