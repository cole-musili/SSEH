from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # --- Dashboard ---
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # --- Quiz Management ---
    path('quizzes/', views.quiz_list_teacher, name='quiz_list_teacher'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/<int:quiz_id>/results/', views.quiz_results_teacher, name='quiz_results_teacher'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),

    # --- Question & Results Management ---
    path('results/<int:result_id>/approve/', views.approve_quiz_result, name='approve_quiz_result'),
    path('quizzes/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path("profile/", views.teacher_profile, name="teacher_profile"),


    path("my-timetable/", views.my_timetable, name="my_timetable"),
]
