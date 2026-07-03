from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    TYPE_LESSON = 'lesson'
    TYPE_ACHIEVEMENT = 'achievement'
    TYPE_CERTIFICATE = 'certificate'
    TYPE_REMINDER = 'reminder'
    TYPE_SYSTEM = 'system'
    TYPE_QUIZ = 'quiz'

    TYPE_CHOICES = [
        (TYPE_LESSON, _('Lesson')),
        (TYPE_ACHIEVEMENT, _('Achievement')),
        (TYPE_CERTIFICATE, _('Certificate')),
        (TYPE_REMINDER, _('Reminder')),
        (TYPE_SYSTEM, _('System')),
        (TYPE_QUIZ, _('Quiz')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_SYSTEM)
    title = models.CharField(_('Title'), max_length=200)
    message = models.TextField(_('Message'))
    icon = models.CharField(_('Icon'), max_length=50, default='🔔')
    link = models.CharField(_('Link'), max_length=500, blank=True)
    is_read = models.BooleanField(_('Read'), default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.title}'

    def mark_as_read(self):
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
