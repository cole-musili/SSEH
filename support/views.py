# support/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ContactMessage
from .forms import ContactMessageForm
from django.core.mail import send_mail
from django.utils import timezone


def is_school_admin(user):
    return user.is_school_admin or user.is_superuser


# 🌍 Public contact form
def contact_admin(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("support:contact_success")
    else:
        form = ContactMessageForm()
    return render(request, "support/contact_admin.html", {"form": form})


# ✅ Contact success page
def contact_success(request):
    return render(request, "support/contact_success.html")


# 📨 Admin Inbox — view all messages
@login_required
@user_passes_test(is_school_admin)
def admin_inbox(request):
    messages_list = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "support/admin_inbox.html", {"messages_list": messages_list})


@login_required
@user_passes_test(is_school_admin)
def reply_message(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)

    if request.method == "POST":
        reply_text = request.POST.get("reply")
        if reply_text:
            # Save reply in DB
            message.reply_text = reply_text
            message.is_replied = True
            message.replied_at = timezone.now()
            message.replied_by = request.user
            message.save()

            messages.success(request, "✅ Reply saved successfully.")
            return redirect("support:admin_inbox")

    # GET request → show reply form
    return render(request, "support/reply_message.html", {"message": message})