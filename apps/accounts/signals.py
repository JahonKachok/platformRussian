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

        try:
            from apps.notifications.utils import notify
            from apps.notifications.models import Notification
            notify(
                user=instance,
                title="Xush kelibsiz!",
                message="LingvoCompetence'ga xush kelibsiz! Rus tilini o'rganishni boshlang.",
                notification_type=Notification.TYPE_SYSTEM,
                icon='👋',
            )
        except Exception:
            pass
