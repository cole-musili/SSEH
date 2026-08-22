from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from accounts.models import User  # import from accounts, not students
from students.models import StudentProfile
from teachers.models import TeacherProfile
from parents.models import ParentProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_student:
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.is_teacher:
            TeacherProfile.objects.get_or_create(user=instance)
        elif instance.is_parent:
            ParentProfile.objects.get_or_create(user=instance)
