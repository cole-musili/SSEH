from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentProfile, QuizResult, Answer
from quizzes.models import Quiz
from accounts.decorators import student_required
from django.contrib.auth.decorators import login_required
from .forms import StudentCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import StudentProfileForm
from school_admin.models import Timetable
from school.models import Enrollment
from .forms import StudentProfileUpdateForm
from django.contrib import messages



@login_required
def student_dashboard(request):
    student_profile, _ = StudentProfile.objects.get_or_create(
        user=request.user
    )

    stream = getattr(student_profile, "stream", None)

    # 1. Fetch all completed quiz results for this student
    completed_results = QuizResult.objects.filter(student=student_profile)

    # 2. Fetch all quizzes (matching take_quiz_list behavior)
    quizzes = Quiz.objects.all().order_by("-created_at")

    quiz_data = []
    completed_percentages = []

    for quiz in quizzes:
        result = completed_results.filter(quiz=quiz).first()

        percentage = None
        total_questions = 0

        if result:
            total_questions = result.answers.count()
            if total_questions > 0:
                percentage = round(
                    (result.score / total_questions) * 100,
                    1
                )
                completed_percentages.append(percentage)

        quiz_data.append({
            "quiz": quiz,
            "result": result,
            "score": result.score if result else None,
            "total_questions": total_questions,
            "percentage": percentage,
        })

    total_quizzes = len(quiz_data)
    completed_count = len(completed_percentages)

    avg_score = (
        round(
            sum(completed_percentages) / completed_count,
            1
        )
        if completed_count > 0
        else 0
    )

    context = {
        "student": student_profile,
        "stream": stream,
        "quizzes": quiz_data,
        "total_quizzes": total_quizzes,
        "completed_count": completed_count,
        "avg_score": avg_score,
    }

    return render(
        request,
        "students/student_dashboard.html",
        context
    )

@student_required
def quiz_result_detail(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student__user=request.user)
    answers = result.answers.select_related("question").all()

    # Calculate percentage safely
    total_questions = answers.count()
    percentage = round((result.score / total_questions) * 100, 1) if total_questions > 0 else 0

    return render(request, "students/quiz_result_detail.html", {
        "result": result,
        "answers": answers,
        "percentage": percentage
    })


@student_required
def take_quiz(request, quiz_id, question_index=0):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    # 🚫 Prevent retaking an already completed quiz
    existing_result = QuizResult.objects.filter(student=student_profile, quiz=quiz).first()
    if existing_result:
        from django.contrib import messages
        messages.info(request, "You have already completed this quiz.")
        return redirect('students:quiz_result_detail', result_id=existing_result.id)

    # Fetch all questions in order
    questions = list(quiz.questions.all().order_by('id'))

    # Initialize quiz answers in session
    if 'quiz_answers' not in request.session:
        request.session['quiz_answers'] = {}

    # Handle form submission
    if request.method == "POST":
        selected_option = request.POST.get('selected_option')
        current_question = questions[question_index]
        request.session['quiz_answers'][str(current_question.id)] = selected_option
        request.session.modified = True

        # Move to next question
        question_index += 1
        if question_index >= len(questions):
            # ✅ Finished quiz → calculate score
            answers = request.session['quiz_answers']
            score = 0
            result = QuizResult.objects.create(student=student_profile, quiz=quiz, score=0)

            for q in questions:
                selected = answers.get(str(q.id))
                is_correct = (selected == q.correct_answer)
                if is_correct:
                    score += 1
                Answer.objects.create(
                    result=result,
                    question=q,
                    selected_option=selected if selected else '',
                    is_correct=is_correct
                )

            result.score = score
            result.save()
            del request.session['quiz_answers']

            from django.contrib import messages
            messages.success(request, f"Quiz completed! Your score: {score}/{len(questions)}")

            return redirect('students:quiz_result_detail', result_id=result.id)

        # 🚀 Redirect to next question
        return redirect('students:take_quiz', quiz_id=quiz.id, question_index=question_index)

    # Safety check: invalid index
    if question_index >= len(questions):
        return redirect('students:student_dashboard')

    context = {
        'quiz': quiz,
        'question': questions[question_index],
        'question_index': question_index,
        'total_questions': len(questions)
    }
    return render(request, 'students/take_quiz.html', context)


@staff_member_required
def create_student(request):
    if request.method == "POST":
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # or wherever you want
    else:
        form = StudentCreationForm()

    return render(request, 'students/create_student.html', {'form': form})


@login_required
def edit_profile(request):
    profile = request.user.student  # thanks to OneToOne
    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("students:student_dashboard")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, "students/edit_profile.html", {"form": form})


@login_required
def results_list(request):
    """Show all quiz results for the logged-in student."""

    student_profile = request.user.studentprofile

    results = (
        student_profile.results
        .select_related("quiz")
        .prefetch_related("answers")
        .order_by("-taken_at")
    )

    result_data = []

    for result in results:

        # Use the actual Answer records belonging to this result.
        total_questions = result.answers.count()

        # Calculate percentage.
        if total_questions > 0:
            percentage = round(
                (result.score / total_questions) * 100,
                1
            )
        else:
            percentage = 0

        result_data.append({
            "id": result.id,
            "quiz": result.quiz,
            "score": result.score,
            "total_questions": total_questions,
            "percentage": percentage,
            "taken_at": result.taken_at,
        })

    percentages = [
        result["percentage"]
        for result in result_data
    ]

    total_results = len(result_data)

    if percentages:
        avg_score = round(
            sum(percentages) / len(percentages),
            1
        )

        best_score = max(percentages)

    else:
        avg_score = 0
        best_score = 0

    context = {
        "results": result_data,
        "avg_score": avg_score,
        "best_score": best_score,
        "total_results": total_results,
    }

    return render(
        request,
        "students/results_list.html",
        context
    )

@login_required
def take_quiz_list(request):
    """
    Show quizzes available for the logged-in student to take.
    """
    student_profile = request.user.studentprofile

    # All completed quizzes by this student
    completed_results = QuizResult.objects.filter(student=student_profile)
    completed_count = completed_results.count()
    taken_ids = completed_results.values_list("quiz_id", flat=True)

    # Quizzes not yet taken
    available_quizzes = Quiz.objects.exclude(id__in=taken_ids).order_by("-created_at")

    # Pending = total available quizzes (not yet done)
    pending_count = available_quizzes.count()

    return render(
        request,
        "students/take_quiz_list.html",
        {
            "quizzes": available_quizzes,
            "completed_count": completed_count,
            "pending_count": pending_count,
        },
    )

@login_required
def class_timetable(request):
    enrollment = Enrollment.objects.filter(student__user=request.user).order_by('-date_enrolled').first()
    entries = Timetable.objects.none()
    if enrollment:
        entries = Timetable.objects.select_related('subject','teacher_record').filter(
            stream=enrollment.stream
        ).order_by('day_of_week','start_time')
    return render(request, "students/class_timetable.html", {"entries": entries, "stream": enrollment.stream if enrollment else None})
@login_required
def profile_settings(request):
    """Allow a student to view and update their profile details."""
    student = request.user.studentprofile
    user = request.user

    if request.method == "POST":
        # Update basic info
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        # Update student-specific info
        student.address = request.POST.get("address", student.address)
        if request.POST.get("date_of_birth"):
            student.date_of_birth = request.POST.get("date_of_birth")

        # Handle profile photo upload
        if "photo" in request.FILES:
            student.photo = request.FILES["photo"]

        student.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("students:profile_settings")

    context = {"student": student}
    return render(request, "students/profile_settings.html", context)

@login_required
def student_timetable(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    stream = student_profile.stream

    if not stream:
        messages.warning(request, "You are not yet assigned to a class stream.")
        return render(request, "students/student_timetable.html", {
            "entries": [],
            "stream": None
        })

    entries = (
        Timetable.objects.filter(stream=stream)
        .select_related("subject", "teacher_record")
        .order_by("day_of_week", "start_time")
    )

    return render(request, "students/student_timetable.html", {
        "entries": entries,
        "stream": stream,
    })
