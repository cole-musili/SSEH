# teachers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from io import BytesIO
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count

from quizzes.models import Quiz, Question
from students.models import QuizResult
from quizzes.forms import QuizForm
from .models import TeacherQuiz, TeacherProfile
from school.models import Stream
from django.contrib.auth import get_user_model
from school_admin.models import TeacherRecord, Timetable
from django.template.loader import get_template
from .forms import TeacherProfileForm

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


User = get_user_model()

@login_required
def teacher_dashboard(request):
    quizzes = TeacherQuiz.objects.filter(teacher=request.user).select_related("quiz", "stream")

    quiz_progress = []
    total_students = 0
    total_attempted = 0
    unique_streams = set()

    for tq in quizzes:
        total = tq.stream.students.count() if tq.stream else 0
        attempted = QuizResult.objects.filter(quiz=tq.quiz).count()

        quiz_progress.append({
            "quiz": tq.quiz,
            "stream": tq.stream,
            "total_students": total,
            "attempted_students": attempted,
        })

        total_students += total
        total_attempted += attempted
        if tq.stream:
            unique_streams.add(tq.stream.id)

    stats = {
        "total_quizzes": len(quiz_progress),
        "total_streams": len(unique_streams),
        "total_students": total_students,
    }

    return render(request, "teachers/teacher_dashboard.html", {
        "quiz_progress": quiz_progress,
        "stats": stats,
    })


# 📋 Teacher Quiz List
@login_required
def quiz_list_teacher(request):
    """Show all quizzes created by this teacher with stats."""
    quizzes = (
        Quiz.objects.filter(created_by=request.user)
        .select_related('teacher_quiz__stream')
        .order_by('-created_at')
    )

    quiz_stats = []
    for quiz in quizzes:
        tq = getattr(quiz, "teacher_quiz", None)
        stream = tq.stream if tq else None
        total_students = stream.students.count() if stream else 0
        attempted = QuizResult.objects.filter(quiz=quiz).count()

        quiz_stats.append({
            "quiz": quiz,
            "stream": stream,
            "total_students": total_students,
            "attempted_students": attempted,
        })

    return render(request, "teachers/quiz_list_teacher.html", {"quiz_stats": quiz_stats})

# ✏️ Create a new quiz
@login_required
def create_quiz(request):
    """Teacher creates a new quiz and assigns it to a stream."""
    if not request.user.is_teacher:
        messages.error(request, "Only teachers can create quizzes.")
        return redirect("accounts:dashboard_redirect")

    assigned_streams = Stream.objects.filter(
        subject_assignments__teacher=request.user
    ).distinct()

    if request.method == "POST":
        form = QuizForm(request.POST)
        stream_id = request.POST.get("stream")
        stream = Stream.objects.filter(id=stream_id).first()

        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()

            TeacherQuiz.objects.get_or_create(
                teacher=request.user,
                quiz=quiz,
                defaults={'stream': stream}
            )

            messages.success(request, f"✅ Quiz '{quiz.title}' created and linked to {stream}.")
            return redirect("teachers:quiz_list_teacher")
    else:
        form = QuizForm()

    return render(request, "teachers/teacher_create_quiz.html", {
        "form": form,
        "streams": assigned_streams
    })


# 📊 View quiz results per stream
@login_required
def quiz_results_teacher(request, quiz_id):
    """
    Show all student results for a quiz within the assigned stream.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    teacher_quiz = get_object_or_404(TeacherQuiz, quiz=quiz, teacher=request.user)
    stream = teacher_quiz.stream

    results = QuizResult.objects.filter(quiz=quiz, student__stream=stream).select_related("student__user")
    students_in_stream = stream.students.all()
    students_taken_ids = results.values_list('student_id', flat=True)
    students_not_taken = students_in_stream.exclude(id__in=students_taken_ids)

    return render(request, "teachers/quiz_results_teacher.html", {
        "quiz": quiz,
        "results": results,
        "has_results": results.exists(),
        "students_not_taken": students_not_taken,
        "stream": stream,
    })


# 🗑️ Delete quiz
@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    if request.method == "POST":
        quiz.delete()
        messages.success(request, f"The quiz '{quiz.title}' was deleted successfully.")
        return redirect(reverse("teachers:quiz_list_teacher"))
    return render(request, "teachers/confirm_delete_quiz.html", {"quiz": quiz})


# ✅ Approve quiz result (for grading control)
@login_required
def approve_quiz_result(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, quiz__created_by=request.user)
    
    if request.method == "POST":
        result.is_approved = True
        result.save()
        messages.success(request, f"Result for {result.student.user.username} approved!")
        return redirect('teachers:quiz_results_teacher', quiz_id=result.quiz.id)

    return render(request, "teachers/approve_result.html", {"result": result})


# ➕ Add questions to quiz
@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    questions = quiz.questions.all().order_by('-id')  # latest first

    if request.method == "POST":
        text = request.POST.get("text")
        option_a = request.POST.get("option_a")
        option_b = request.POST.get("option_b")
        option_c = request.POST.get("option_c")
        option_d = request.POST.get("option_d")
        correct_answer = request.POST.get("correct_answer")

        if text and correct_answer:
            Question.objects.create(
                quiz=quiz,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer
            )
            messages.success(request, "✅ Question added successfully!")
            return redirect("teachers:add_question", quiz_id=quiz.id)

    return render(request, "teachers/add_question.html", {
        "quiz": quiz,
        "questions": questions
    })

@login_required
def my_timetable(request):
    # try find linked teacher record
    tr = TeacherRecord.objects.filter(user=request.user).first()
    entries = Timetable.objects.none()
    if tr:
        entries = Timetable.objects.select_related('stream','subject').filter(teacher_record=tr).order_by('day_of_week','start_time')
    return render(request, "teachers/my_timetable.html", {"entries": entries, "tr": tr})

@login_required
def teacher_profile(request):
    """Display and update teacher profile (photo only)."""
    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("teachers:teacher_dashboard")

    user = request.user

    # Handle photo upload
    if request.method == "POST":
        if "profile_picture" in request.FILES:
            user.profile_picture = request.FILES["profile_picture"]
            user.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("teachers:teacher_profile")

    context = {
        "teacher_profile": teacher_profile,
        "teacher": user,
    }
    return render(request, "teachers/profile.html", context)


@login_required
def my_timetable(request):
    """Display the teacher’s timetable with optional day filtering and PDF export."""
    from io import BytesIO
    from django.http import FileResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    teacher_record = TeacherRecord.objects.filter(user=request.user).first()
    entries = Timetable.objects.none()
    selected_day = request.GET.get("day", "")  # Optional filter

    if teacher_record:
        entries = (
            Timetable.objects
            .select_related("stream", "subject")
            .filter(teacher_record=teacher_record)
            .order_by("day_of_week", "start_time")
        )
        if selected_day:
            entries = entries.filter(day_of_week=selected_day)

    # PDF Export Option
    if request.GET.get("export") == "pdf" and entries.exists():
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, height - 80, f"Teacher Timetable - {request.user.get_full_name() or request.user.username}")

        p.setFont("Helvetica", 10)
        y = height - 120
        p.drawString(60, y, "Day")
        p.drawString(150, y, "Time")
        p.drawString(250, y, "Subject")
        p.drawString(400, y, "Stream")

        y -= 20
        for e in entries:
            if y < 50:  # new page
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 80
            p.drawString(60, y, e.get_day_of_week_display())
            p.drawString(150, y, f"{e.start_time} - {e.end_time}")
            p.drawString(250, y, e.subject.name)
            p.drawString(400, y, f"{e.stream.grade.name} {e.stream.code}")
            y -= 18

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="teacher_timetable.pdf")

    days = [
        ("", "All Days"),
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
    ]

    context = {
        "entries": entries,
        "teacher_record": teacher_record,
        "selected_day": selected_day,
        "days": days,
    }
    return render(request, "teachers/my_timetable.html", context)
