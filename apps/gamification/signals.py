from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='gamification.UserProgress')
def check_achievements(sender, instance, **kwargs):
    pass
