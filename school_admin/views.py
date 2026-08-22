# school_admin/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import User
from school.models import GradeLevel, Stream, Subject, TeacherAssignment, AcademicYear, Term
from students.models import StudentProfile
from .models import TeacherRecord
from .forms import TeacherRecordForm
from .models import Timetable
from .forms import TimetableForm
from .models import AcademicYear, Term
from .forms import AcademicYearForm, TermForm
from announcements.models import Announcement
from .models import Timetable, AcademicYear, Term
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from collections import OrderedDict
from teachers.models import TeacherProfile
from parents.models import ParentProfile


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# ✅ Helper: Only school_admin flag OR superuser can access the custom panel
def is_school_admin(user):
    return user.is_superuser or getattr(user, "is_school_admin", False)



# 🧱 Forms
class GradeForm(forms.ModelForm):
    class Meta:
        model = GradeLevel
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ["grade", "code", "year", "homeroom_teacher"]
        widgets = {
            "grade": forms.Select(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.Select(attrs={"class": "form-control"}),
            "homeroom_teacher": forms.Select(attrs={"class": "form-control"}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ["teacher", "subject", "stream", "term"]
        widgets = {
            "teacher": forms.Select(attrs={"class": "form-control"}),
            "subject": forms.Select(attrs={"class": "form-control"}),
            "stream": forms.Select(attrs={"class": "form-control"}),
            "term": forms.Select(attrs={"class": "form-control"}),
        }


# 🏫 Admin Dashboard
@login_required
@user_passes_test(is_school_admin)
def admin_dashboard(request):
    grades = GradeLevel.objects.all()
    streams = Stream.objects.select_related("grade", "homeroom_teacher")
    subjects = Subject.objects.all()
    teachers = User.objects.filter(is_teacher=True)
    students = User.objects.filter(is_student=True)
    profile = request.user.school_admin_profile

    # Academic year & term
    current_year = AcademicYear.objects.filter(is_active=True).first()
    current_term = Term.objects.filter(is_current=True, academic_year=current_year).first() if current_year else None

    # Announcements (latest 5)
    announcements = Announcement.objects.filter(is_published=True).order_by("-created_at")[:5]

    # Timetable preview (next 5)
    upcoming_timetable = Timetable.objects.select_related("stream", "subject").order_by("day_of_week", "start_time")[:5]

    context = {
        "grade_count": grades.count(),
        "stream_count": streams.count(),
        "teacher_count": teachers.count(),
        "student_count": students.count(),
        "grades": grades,
        "streams": streams,
        "current_year": current_year,
        "current_term": current_term,
        "announcements": announcements,
        "upcoming_timetable": upcoming_timetable,
        "profile": profile,
    }

    return render(request, "school_admin/dashboard.html", context)

# ➕ Create Grade
@login_required
@user_passes_test(is_school_admin)
def create_grade(request):
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Grade created successfully!")
            return redirect("school_admin:admin_dashboard")
    else:
        form = GradeForm()
    return render(request, "school_admin/create_grade.html", {"form": form})


# ➕ Create Stream
@login_required
@user_passes_test(is_school_admin)
def create_stream(request):
    if request.method == "POST":
        form = StreamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Stream created successfully!")
            return redirect("school_admin:admin_dashboard")
    else:
        form = StreamForm()
    return render(request, "school_admin/create_stream.html", {"form": form})


# 👩‍🏫 Assign Teacher to Subject/Stream
@login_required
@user_passes_test(is_school_admin)
def assign_teacher(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Teacher assignment created successfully!")
            return redirect("school_admin:assign_teacher")
    else:
        form = AssignmentForm()

    assignments = TeacherAssignment.objects.select_related("teacher", "subject", "stream", "term")
    return render(request, "school_admin/assign_teacher.html", {
        "form": form,
        "assignments": assignments,
    })


# 🧑‍🏫 Create New Teacher Account
@login_required
@user_passes_test(is_school_admin)
def create_teacher(request):
    subjects = Subject.objects.all()
    streams = Stream.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        specialization_id = request.POST.get("specialization")
        stream_ids = request.POST.getlist("streams")

        if not username or not password:
            messages.error(request, "⚠️ Username and password are required.")
            return redirect("school_admin:create_teacher")

        # Create the teacher account
        user = User.objects.create_user(username=username, email=email, password=password, is_teacher=True)
        specialization = Subject.objects.filter(id=specialization_id).first()

        teacher_record = TeacherRecord.objects.create(
            user=user,
            phone=phone,
            specialization=specialization
        )
        teacher_record.assigned_streams.set(stream_ids)

        messages.success(request, f"✅ Teacher '{username}' created successfully!")
        return redirect("school_admin:teacher_records")

    return render(request, "school_admin/create_teacher.html", {
        "subjects": subjects,
        "streams": streams,
    })


# 🧑‍🏫 Manage Existing Teacher Records
@login_required
@user_passes_test(is_school_admin)
def teacher_records(request):
    teachers = TeacherRecord.objects.select_related("user", "specialization").prefetch_related("assigned_streams")

    if request.method == "POST":
        user_id = request.POST.get("user")
        phone = request.POST.get("phone")
        specialization_id = request.POST.get("specialization")
        streams_ids = request.POST.getlist("streams")

        if user_id:
            user = User.objects.get(id=user_id)
            specialization = Subject.objects.filter(id=specialization_id).first()
            teacher_record, created = TeacherRecord.objects.get_or_create(
                user=user,
                defaults={"phone": phone, "specialization": specialization},
            )
            if not created:
                teacher_record.phone = phone
                teacher_record.specialization = specialization
                teacher_record.save()
            teacher_record.assigned_streams.set(streams_ids)
            messages.success(request, f"✅ Teacher record for {user.username} saved successfully!")
            return redirect("school_admin:teacher_records")

    available_users = User.objects.filter(is_teacher=True).exclude(teacherrecord__isnull=False)
    subjects = Subject.objects.all()
    streams = Stream.objects.all()

    return render(request, "school_admin/teacher_records.html", {
        "teachers": teachers,
        "available_users": available_users,
        "subjects": subjects,
        "streams": streams,
    })

@login_required
@user_passes_test(is_school_admin)
def teacher_record_list(request):
    teachers = TeacherRecord.objects.select_related('specialization').prefetch_related('assigned_streams')
    return render(request, 'school_admin/teacher_record_list.html', {'teachers': teachers})


@login_required
@user_passes_test(is_school_admin)
def create_teacher_record(request):
    if request.method == 'POST':
        form = TeacherRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Teacher record created successfully!")
            return redirect('school_admin:teacher_record_list')
    else:
        form = TeacherRecordForm()

    return render(request, 'school_admin/create_teacher_record.html', {'form': form})

@login_required
@user_passes_test(is_school_admin)
def teacher_detail(request, pk):
    teacher = get_object_or_404(TeacherRecord, pk=pk)
    subjects = Subject.objects.all()
    streams = Stream.objects.all()

    if request.method == "POST":
        teacher.full_name = request.POST.get("full_name")
        teacher.phone = request.POST.get("phone")
        teacher.email = request.POST.get("email")
        teacher.gender = request.POST.get("gender")
        teacher.qualification = request.POST.get("qualification")
        teacher.status = request.POST.get("status")
        teacher.specialization_id = request.POST.get("specialization") or None
        teacher.save()
        teacher.assigned_streams.set(request.POST.getlist("streams"))

        messages.success(request, "✅ Teacher details updated successfully!")
        return redirect("school_admin:teacher_detail", pk=teacher.pk)

    return render(request, "school_admin/teacher_detail.html", {
        "teacher": teacher,
        "subjects": subjects,
        "streams": streams,
    })

@login_required
@user_passes_test(is_school_admin)
def timetable_list(request):
    entries = Timetable.objects.all().select_related("stream", "subject", "teacher_record")
    streams = Stream.objects.all()
    return render(request, "school_admin/timetable_list.html", {"entries": entries, "streams": streams})

@login_required
@user_passes_test(is_school_admin)
def timetable_create(request):
    if request.method == "POST":
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Timetable entry created.")
            return redirect("school_admin:timetable_list")
    else:
        form = TimetableForm()
    return render(request, "school_admin/timetable_form.html", {"form": form, "mode": "Create"})

@login_required
@user_passes_test(is_school_admin)
def timetable_edit(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    if request.method == "POST":
        form = TimetableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Timetable entry updated.")
            return redirect("school_admin:timetable_list")
    else:
        form = TimetableForm(instance=entry)
    return render(request, "school_admin/timetable_form.html", {"form": form, "mode": "Edit"})


@login_required
@user_passes_test(is_school_admin)
def timetable_stream_view(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    # Fetch entries for this stream ordered by start time
    qs = Timetable.objects.filter(stream=stream).select_related('subject', 'teacher_record').order_by('day_of_week', 'start_time')

    # Map short day codes to full labels
    day_map = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday"}

    # Build ordered dict with entries per day
    timetable_data = OrderedDict((day, []) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    for e in qs:
        label = day_map.get(e.day_of_week, e.day_of_week)
        if label in timetable_data:
            timetable_data[label].append(e)

    # Find maximum rows needed across all days
    max_rows_count = max([len(entries) for entries in timetable_data.values()] + [1])
    max_rows = range(max_rows_count)

    # Context data for modal dropdowns
    subjects = Subject.objects.all()
    teachers = TeacherRecord.objects.all()

    return render(request, "school_admin/timetable_stream_view.html", {
        "stream": stream,
        "timetable_data": timetable_data,
        "max_rows": max_rows,
        "subjects": subjects,
        "teachers": teachers,
    })

@login_required
@user_passes_test(is_school_admin)
def academic_year_list(request):
    years = AcademicYear.objects.all()
    return render(request, "school_admin/academic_year_list.html", {"years": years})


@login_required
@user_passes_test(is_school_admin)
def academic_year_create(request):
    if request.method == "POST":
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.is_active:
                AcademicYear.objects.update(is_active=False)
            instance.save()
            messages.success(request, "Academic Year created successfully.")
            return redirect("school_admin:academic_year_list")
    else:
        form = AcademicYearForm()
    return render(request, "school_admin/academic_year_form.html", {"form": form, "mode": "Create"})


@login_required
@user_passes_test(is_school_admin)
def term_list(request):
    terms = Term.objects.select_related("academic_year")
    return render(request, "school_admin/term_list.html", {"terms": terms})


@login_required
@user_passes_test(is_school_admin)
def term_create(request):
    if request.method == "POST":
        form = TermForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Term created successfully.")
            return redirect("school_admin:term_list")
    else:
        form = TermForm()
    return render(request, "school_admin/term_form.html", {"form": form, "mode": "Create"})


@login_required
@user_passes_test(is_school_admin)
def profile_settings(request):
    profile = request.user.school_admin_profile

    # 🔁 Handle profile update
    if request.method == "POST" and "update_profile" in request.POST:
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        status = request.POST.get("status")
        photo = request.FILES.get("photo")

        # Save text fields
        profile.full_name = full_name
        profile.phone = phone
        profile.status = status

        # Handle photo upload + sync to User.profile_picture
        if photo:
            profile.photo = photo
            request.user.profile_picture = photo  # ✅ sync with User model
            request.user.save()
        profile.save()

        messages.success(request, "✅ Profile updated successfully.")
        return redirect("school_admin:profile_settings")

    # 🔐 Handle password change separately
    if request.method == "POST" and "change_password" in request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # prevent logout
            messages.success(request, "🔐 Password updated successfully.")
            return redirect("school_admin:profile_settings")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "school_admin/profile_settings.html",
        {"profile": profile, "form": form},
    )

@login_required
@user_passes_test(is_school_admin)
def manage_user_status(request):
    teachers = TeacherProfile.objects.select_related('user').all()
    students = StudentProfile.objects.select_related('user').all()
    parents = ParentProfile.objects.select_related('user').all()

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('status')

        if user_type == 'teacher':
            profile = TeacherProfile.objects.get(id=user_id)
        elif user_type == 'student':
            profile = StudentProfile.objects.get(id=user_id)
        elif user_type == 'parent':
            profile = ParentProfile.objects.get(id=user_id)
        else:
            profile = None

        if profile:
            profile.status = new_status
            profile.save()
            messages.success(request, f"{profile.user.username}'s status updated to {new_status} ✅")
        return redirect('school_admin:manage_user_status')

    return render(request, 'school_admin/manage_user_status.html', {
        'teachers': teachers,
        'students': students,
        'parents': parents
    })
