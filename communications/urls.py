# communications/urls.py
from django.urls import path
from . import views

app_name = "communications"

urlpatterns = [
    # Teacher communication
    path("teacher/messages/", views.teacher_message_list, name="teacher_message_list"),  # 📬 list sent messages
    path("teacher/messages/send/", views.teacher_send_message, name="teacher_send_message"),  # ✉️ send new message
    path("teacher/messages/<int:pk>/", views.teacher_message_detail, name="teacher_message_detail"), # 📄 detail

    # Parent communication
    path("parent/messages/", views.parent_message_list, name="parent_message_list"),  # 📥 inbox
    path("parent/messages/<int:message_id>/", views.parent_message_detail, name="parent_message_detail"), # 📄 detail
     

        # 🧩 Add this new route for students
    path("student/messages/", views.student_message_list, name="student_message_list"),
    path("student/messages/<int:pk>/", views.student_message_detail, name="student_message_detail"),
]
