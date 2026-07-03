from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            from apps.gamification.models import UserProgress
            UserProgress.objects.get_or_create(user=instance)
        except Exception:
            pass
