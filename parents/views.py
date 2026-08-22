from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from students.models import StudentProfile, QuizResult
from .models import ParentProfile
from .forms import ParentProfileForm

@login_required
def parent_dashboard(request):
    # Get the parent profile linked to the current user
    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    linked_students = parent_profile.students.all()

    student_data = []
    for student in linked_students:
        results = QuizResult.objects.filter(student=student, is_approved=True).select_related('quiz')
        student_data.append({
            "student": student,
            "results": results
        })

    return render(request, "parents/parent_dashboard.html", {
        "parent": parent_profile,
        "student_data": student_data,
    })

@login_required
def profile_settings(request):
    profile, _ = ParentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ParentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("parents:profile_settings")
    else:
        form = ParentProfileForm(instance=profile)

    return render(request, "parents/profile_settings.html", {
        "form": form,
        "profile": profile,  # ✅ Add this line
    })
