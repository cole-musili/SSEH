from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('accounts:dashboard_redirect')

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    """Redirect users based on their role."""

    user = request.user

    if user.is_school_admin:
        return redirect('school_admin:admin_dashboard')

    elif user.is_teacher:
        return redirect('teachers:teacher_dashboard')

    elif user.is_student:
        return redirect('students:student_dashboard')

    elif user.is_parent:
        return redirect('parents:parent_dashboard')

    else:
        return render(request, 'accounts/unknown_role.html')


@login_required
def change_password(request):
    """Allow logged-in users to change their password."""

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Your password was changed successfully."
            )

            return redirect(
                "students:profile_settings"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )