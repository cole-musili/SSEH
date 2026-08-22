# quizzes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question
from accounts.models import User
from students.models import StudentProfile, QuizResult, Answer
from .forms import QuestionForm



# ---------- Teacher Side ----------

@login_required
def create_quiz(request):
    if not request.user.is_teacher:
        return redirect("quizzes:quiz_list")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        quiz = Quiz.objects.create(
            title=title, description=description, created_by=request.user
        )
        return redirect("quizzes:add_question", quiz_id=quiz.id)

    return render(request, "quizzes/create_quiz.html")


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('quizzes:add_question', quiz_id=quiz.id)
    else:
        form = QuestionForm()

    # List all questions added for this quiz
    questions = quiz.questions.all()

    return render(request, 'quizzes/add_question.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions
    })

@login_required
def quiz_results(request, quiz_id):
    # Ensure only the teacher who created the quiz can view results
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    # Get all QuizResults for this quiz
    results = QuizResult.objects.filter(quiz=quiz).select_related("student__user").prefetch_related("answers__question")

    context = {
        "quiz": quiz,
        "results": results,
    }
    return render(request, "quizzes/quiz_results.html", context)


@login_required
def quiz_list(request):
    # Students see all quizzes
    if request.user.is_student:
        quizzes = Quiz.objects.all()
    else:
        # Teachers see only their own quizzes
        quizzes = Quiz.objects.filter(created_by=request.user)

    return render(request, "quizzes/quiz_list.html", {"quizzes": quizzes})


@login_required
def take_quiz(request, quiz_id, question_index=0):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())

    # Redirect if no questions
    if not questions:
        return render(request, "quizzes/take_quiz.html", {"quiz": quiz, "error": "No questions yet."})

    # Ensure question_index is integer
    question_index = int(question_index)

    # Initialize session storage for answers
    if "quiz_answers" not in request.session:
        request.session["quiz_answers"] = {}

    if request.method == "POST":
        selected_option = request.POST.get("selected_option")
        # Store the answer in session
        request.session["quiz_answers"][str(question_index)] = selected_option
        request.session.modified = True

        # Go to next question
        if question_index + 1 < len(questions):
            return redirect("quizzes:take_quiz", quiz_id=quiz.id, question_index=question_index + 1)
        else:
            # Last question -> calculate score
            score = 0
            student_profile = StudentProfile.objects.get(user=request.user)
            result = QuizResult.objects.create(student=student_profile, quiz=quiz, score=0)
            
            for idx, question in enumerate(questions):
                selected = request.session["quiz_answers"].get(str(idx))
                is_correct = selected == question.correct_answer
                if is_correct:
                    score += 1
                Answer.objects.create(result=result, question=question, selected_option=selected or "", is_correct=is_correct)

            result.score = score
            result.save()

            # Clear session
            del request.session["quiz_answers"]

            return render(request, "quizzes/quiz_result.html", {"quiz": quiz, "score": score, "total": len(questions)})

    current_question = questions[question_index]

    return render(request, "quizzes/take_quiz.html", {
        "quiz": quiz,
        "question": current_question,
        "question_number": question_index + 1,
        "total_questions": len(questions),
    })

@login_required
def quiz_result_detail(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student__user=request.user if request.user.is_student else None)
    
    # If teacher, ensure they own the quiz
    if request.user.is_teacher and result.quiz.created_by != request.user:
        return redirect("quizzes:quiz_list")

    answers = result.answers.select_related("question").all()

    return render(request, "quizzes/quiz_result_detail.html", {
        "result": result,
        "answers": answers,
    })
