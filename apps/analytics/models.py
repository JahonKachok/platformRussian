from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class StudySession(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_sessions'
    )
    date = models.DateField(_('Date'))
    minutes_studied = models.PositiveIntegerField(_('Minutes Studied'), default=0)
    xp_earned = models.PositiveIntegerField(_('XP Earned'), default=0)
    lessons_completed = models.PositiveSmallIntegerField(_('Lessons Completed'), default=0)
    quizzes_completed = models.PositiveSmallIntegerField(_('Quizzes Completed'), default=0)
    words_reviewed = models.PositiveSmallIntegerField(_('Words Reviewed'), default=0)

    class Meta:
        verbose_name = _('Study Session')
        verbose_name_plural = _('Study Sessions')
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} - {self.date} ({self.minutes_studied}m)'
