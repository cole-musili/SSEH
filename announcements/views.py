# announcements/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Announcement
from .forms import AnnouncementForm

# 🔒 Access check — only school admins or superusers
def is_school_admin(user):
    return user.is_school_admin or user.is_superuser


# 🌍 Public: visible to all roles
@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(is_published=True)
    return render(request, "announcements/announcement_list.html", {
        "announcements": announcements
    })


# 🏫 Admin: view/manage announcements
@login_required
@user_passes_test(is_school_admin)
def manage_announcements(request):
    announcements = Announcement.objects.all()
    return render(request, "announcements/manage_announcements.html", {
        "announcements": announcements
    })


# ➕ Create new announcement
@login_required
@user_passes_test(is_school_admin)
def create_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.posted_by = request.user
            ann.save()
            messages.success(request, "Announcement created successfully.")
            return redirect("announcements:manage_announcements")
    else:
        form = AnnouncementForm()
    return render(request, "announcements/announcement_form.html", {
        "form": form,
        "mode": "Create",
    })


# ✏️ Edit existing
@login_required
@user_passes_test(is_school_admin)
def edit_announcement(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES, instance=ann)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect("announcements:manage_announcements")
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, "announcements/announcement_form.html", {
        "form": form,
        "mode": "Edit",
    })


# ❌ Delete confirmation
@login_required
@user_passes_test(is_school_admin)
def delete_announcement(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        ann.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect("announcements:manage_announcements")
    return render(request, "announcements/announcement_confirm_delete.html", {
        "announcement": ann
    })

# 📰 View single announcement detail
def announcement_detail(request, pk):
    ann = get_object_or_404(Announcement, pk=pk, is_published=True)
    return render(request, "announcements/announcement_detail.html", {"ann": ann})

