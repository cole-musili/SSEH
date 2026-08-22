from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings



def home_redirect(request):
    return redirect("accounts:dashboard_redirect")  # 👈 or another view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("quizzes/", include(("quizzes.urls", "quizzes"), namespace="quizzes")),
    path("students/", include(("students.urls", "students"), namespace="students")),
    path("teachers/", include(("teachers.urls", "teachers"), namespace="teachers")),
    path("parents/", include(("parents.urls", "parents"), namespace="parents")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("", home_redirect, name="home"),
    path('school-admin/', include('school_admin.urls')),
    path("communications/", include("communications.urls")),
    path("resources/", include("resources.urls")),
    path("announcements/", include("announcements.urls")),
    path("support/", include("support.urls"))

  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)