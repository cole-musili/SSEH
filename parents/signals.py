from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ParentProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_parent_profile(sender, instance, created, **kwargs):
    if created:
        is_parent_flag = getattr(instance, 'is_parent', False)
        has_parent_role = getattr(instance, 'role', None) == 'PARENT'
        
        if is_parent_flag or has_parent_role:
            ParentProfile.objects.get_or_create(user=instance)