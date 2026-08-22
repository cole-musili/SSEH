from django.urls import path
from . import views

app_name = "parents"

urlpatterns = [
    path("dashboard/", views.parent_dashboard, name="parent_dashboard"),
    path("profile/", views.profile_settings, name="profile_settings"),
]
