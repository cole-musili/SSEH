# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps  # ✅ safer dynamic import

class User(AbstractUser):
    # Role flags
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)

    # Shared profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_school_admin_profile(sender, instance, created, **kwargs):
    """
    Automatically create a SchoolAdminProfile when a user is marked as a school admin.
    """
    if instance.is_school_admin:
        # ✅ safe dynamic import to avoid circular dependency
        SchoolAdminProfile = apps.get_model('school_admin', 'SchoolAdminProfile')
        SchoolAdminProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def ensure_school_admin_not_superuser(sender, instance, **kwargs):
    """
    Ensure no school admin ever becomes a Django superuser or staff.
    """
    if instance.is_school_admin:
        if instance.is_superuser or instance.is_staff:
            instance.is_superuser = False
            instance.is_staff = False
            instance.save()

