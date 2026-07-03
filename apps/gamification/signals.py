from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='gamification.UserProgress')
def check_achievements(sender, instance, **kwargs):
    try:
        from .models import Achievement, UserAchievement
        from apps.notifications.utils import notify
        from apps.notifications.models import Notification

        user = instance
        already_earned = set(
            UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
        )

        candidates = Achievement.objects.exclude(id__in=already_earned)

        for achievement in candidates:
            earned = False
            ct = achievement.condition_type
            cv = achievement.condition_value

            if ct == 'lessons_completed':
                earned = instance.total_lessons_completed >= cv
            elif ct == 'quizzes_completed':
                earned = instance.total_quizzes_completed >= cv
            elif ct == 'words_learned':
                earned = instance.total_words_learned >= cv
            elif ct == 'streak_days':
                earned = instance.streak_days >= cv
            elif ct == 'xp_total':
                earned = instance.xp >= cv
            elif ct == 'level':
                earned = instance.level >= cv

            if earned:
                UserAchievement.objects.create(user=user, achievement=achievement)
                instance.add_xp(achievement.xp_reward, 'achievement')
                instance.add_coins(achievement.coin_reward)

                notify(
                    user=user,
                    title=f'Yangi yutuq: {achievement.name}',
                    message=f'{achievement.description} +{achievement.xp_reward} XP, +{achievement.coin_reward} tanga.',
                    notification_type=Notification.TYPE_ACHIEVEMENT,
                    icon=achievement.icon or '🏆',
                )
    except Exception:
        pass
