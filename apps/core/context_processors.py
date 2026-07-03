from django.conf import settings
from django.utils.translation import get_language


def global_context(request):
    ctx = {
        'SITE_NAME': 'LingvoCompetence',
        'SITE_TAGLINE': 'Rus tilini o\'rganing',
        'CURRENT_LANGUAGE': get_language(),
        'LANGUAGES': settings.LANGUAGES,
        'DEBUG': settings.DEBUG,
    }

    if request.user.is_authenticated:
        try:
            from apps.gamification.models import UserProgress
            progress = UserProgress.objects.select_related('user').get(user=request.user)
            ctx['user_xp'] = progress.xp
            ctx['user_level'] = progress.level
            ctx['user_coins'] = progress.coins
            ctx['user_streak'] = progress.streak_days
        except Exception:
            ctx['user_xp'] = 0
            ctx['user_level'] = 1
            ctx['user_coins'] = 0
            ctx['user_streak'] = 0

        try:
            from apps.notifications.models import Notification
            ctx['unread_notifications'] = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            ctx['unread_notifications'] = 0

    return ctx
