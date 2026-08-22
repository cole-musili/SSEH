from functools import wraps
from django.shortcuts import redirect

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher:
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student:
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def parent_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_parent:
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
