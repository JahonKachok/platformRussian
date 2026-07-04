from django.conf import settings
from django.utils.translation import get_language

# Single source of truth for language display metadata. Any language code
# missing here (e.g. a new one added to settings.LANGUAGES) still renders
# safely via the fallback in _language_info() instead of breaking templates.
LANGUAGE_META = {
    'uz': {'flag': '🇺🇿', 'short': "O'z", 'name': "O'zbek"},
    'en': {'flag': '🇬🇧', 'short': 'En', 'name': 'English'},
    'ru': {'flag': '🇷🇺', 'short': 'Ru', 'name': 'Русский'},
}


def _language_info(code, fallback_name):
    meta = LANGUAGE_META.get(code, {})
    return {
        'code': code,
        'flag': meta.get('flag', '🌐'),
        'short': meta.get('short', code.upper()),
        'name': meta.get('name', fallback_name),
    }


def global_context(request):
    current_language = get_language()
    language_choices = [_language_info(code, name) for code, name in settings.LANGUAGES]
    current_language_info = next(
        (lang for lang in language_choices if lang['code'] == current_language),
        _language_info(current_language, current_language),
    )

    ctx = {
        'SITE_NAME': 'LingvoCompetence',
        'SITE_TAGLINE': 'Rus tilini o\'rganing',
        'CURRENT_LANGUAGE': current_language,
        'CURRENT_LANGUAGE_INFO': current_language_info,
        'LANGUAGE_CHOICES': language_choices,
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
