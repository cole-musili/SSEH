# announcements/urls.py
from django.urls import path
from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.announcement_list, name="list"),
    path("manage/", views.manage_announcements, name="manage_announcements"),
    path("create/", views.create_announcement, name="create_announcement"),
    path("<int:pk>/", views.announcement_detail, name="detail"), 
    path("<int:pk>/edit/", views.edit_announcement, name="edit_announcement"),
    path("<int:pk>/delete/", views.delete_announcement, name="delete_announcement"),
]

