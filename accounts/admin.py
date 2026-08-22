from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = (
        'username', 'first_name', 'last_name', 'email', 'colored_role',
        'is_active', 'is_staff', 'is_superuser',
    )
    list_filter = (
        'is_teacher', 'is_student', 'is_parent', 'is_school_admin',
        'is_staff', 'is_superuser', 'is_active'
    )

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'profile_picture')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Roles', {
            'fields': (
                'is_teacher',
                'is_student',
                'is_parent',
                'is_school_admin',
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                'is_teacher', 'is_student', 'is_parent', 'is_school_admin'
            ),
        }),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def colored_role(self, obj):
        """Return colored badges for roles."""
        if obj.is_school_admin:
            color, label = '#0ea5e9', 'School Admin'
        elif obj.is_teacher:
            color, label = '#16a34a', 'Teacher'
        elif obj.is_student:
            color, label = '#2563eb', 'Student'
        elif obj.is_parent:
            color, label = '#9333ea', 'Parent'
        elif obj.is_superuser:
            color, label = '#dc2626', 'Superuser'
        elif obj.is_staff:
            color, label = '#f59e0b', 'Staff'
        else:
            color, label = '#6b7280', 'User'

        return format_html(
            f'<span style="background:{color}; color:white; padding:2px 8px; '
            f'border-radius:8px; font-size:12px;">{label}</span>'
        )

    colored_role.short_description = "Role"
    colored_role.admin_order_field = 'is_school_admin'