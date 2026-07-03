from .models import Notification


def notify(user, title, message, notification_type=Notification.TYPE_SYSTEM, icon='🔔', link=''):
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            icon=icon,
            link=link,
        )
    except Exception:
        pass
