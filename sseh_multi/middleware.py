# sseh_multi/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class ForceHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "text/plain" in response.get("Content-Type", ""):
            response["Content-Type"] = "text/html; charset=utf-8"
        return response
    

class SuperuserOnlyAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return self.get_response(request)
            if not request.user.is_superuser:
                return redirect('school_admin:admin_dashboard')
        return self.get_response(request)