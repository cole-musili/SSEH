# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")


@login_required
def teacher_dashboard(request):
    return render(request, "dashboard/teacher_dashboard.html")


@login_required
def student_dashboard(request):
    return render(request, "dashboard/student_dashboard.html")


@login_required
def parent_dashboard(request):
    return render(request, "dashboard/parent_dashboard.html")
