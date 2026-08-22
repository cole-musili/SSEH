from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    # Teacher side
    path("create/", views.create_quiz, name="create_quiz"),
    path("<int:quiz_id>/add-question/", views.add_question, name="add_question"),
    path("<int:quiz_id>/results/", views.quiz_results, name="quiz_results"),

    # Student side
    path("", views.quiz_list, name="quiz_list"),
    path("<int:quiz_id>/take/", views.take_quiz, name="take_quiz"),
]
