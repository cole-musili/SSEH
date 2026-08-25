from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from students.models import QuizResult
from .models import ParentProfile
from .forms import ParentProfileForm

@login_required
def parent_dashboard(request):
    if not hasattr(request.user, 'parentprofile'):
        raise PermissionDenied("You do not have permission to access the Parent Portal.")
    
    parent_profile = request.user.parentprofile
    linked_students = parent_profile.students.all() if hasattr(parent_profile, 'students') else []

    student_data = []
    for student in linked_students:
        results = QuizResult.objects.filter(student=student).select_related('quiz')
        
        quiz_list = []
        percentages = []
        
        for res in results:
            # Count answers associated with this result (or fallback to quiz total)
            total_q = res.answers.count() if hasattr(res, 'answers') else 0
            
            percentage = None
            if total_q > 0:
                percentage = round((res.score / total_q) * 100, 1)
                percentages.append(percentage)
                
            quiz_list.append({
                "result": res,
                "quiz": res.quiz,
                "score": res.score,
                "total_questions": total_q,
                "percentage": percentage,
            })

        avg_score = round(sum(percentages) / len(percentages), 1) if percentages else 0

        student_data.append({
            "student": student,
            "quizzes": quiz_list,
            "total_quizzes_taken": len(quiz_list),
            "avg_score": avg_score,
        })

    return render(request, "parents/parent_dashboard.html", {
        "parent": parent_profile,
        "student_data": student_data,
    })

@login_required
def profile_settings(request):
    # Fetch profile or return 404 if it doesn't exist
    profile = get_object_or_404(ParentProfile, user=request.user)

    if request.method == "POST":
        form = ParentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("parents:profile_settings")
    else:
        form = ParentProfileForm(instance=profile)

    return render(request, "parents/profile_settings.html", {
        "form": form,
        "profile": profile,
    })