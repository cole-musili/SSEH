# students/urls.py
from django.urls import path
from . import views

# Namespace for student URLs
app_name = "students"

urlpatterns = [
    # Student Dashboard
    path("", views.student_dashboard, name="student_dashboard"),
    

    # Take a quiz (one question at a time)
    path("take/<int:quiz_id>/<int:question_index>/", views.take_quiz, name="take_quiz"),
    path("take/<int:quiz_id>/", views.take_quiz, name="take_quiz_start"),  # starts from question_index=0

    # View quiz result detail
    path("quizzes/", views.take_quiz_list, name="take_quiz_list"),
    path("results/<int:result_id>/", views.quiz_result_detail, name="quiz_result_detail"),

    path("results/", views.results_list, name="results"),
    path("profile/settings/", views.profile_settings, name="profile_settings"),


    path("timetable/", views.student_timetable, name="student_timetable"),



]
