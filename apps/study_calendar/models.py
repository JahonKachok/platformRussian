from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class CalendarEvent(TimeStampedModel):
    TYPE_LESSON = 'lesson'
    TYPE_QUIZ = 'quiz'
    TYPE_ASSIGNMENT = 'assignment'
    TYPE_REMINDER = 'reminder'
    TYPE_HOLIDAY = 'holiday'
    TYPE_GOAL = 'goal'
    TYPE_COMPLETED = 'completed'

    TYPE_CHOICES = [
        (TYPE_LESSON, _('Lesson')),
        (TYPE_QUIZ, _('Quiz')),
        (TYPE_ASSIGNMENT, _('Assignment')),
        (TYPE_REMINDER, _('Reminder')),
        (TYPE_HOLIDAY, _('Holiday')),
        (TYPE_GOAL, _('Goal')),
        (TYPE_COMPLETED, _('Completed')),
    ]

    TYPE_COLORS = {
        TYPE_LESSON: '#6366f1',
        TYPE_QUIZ: '#f59e0b',
        TYPE_ASSIGNMENT: '#8b5cf6',
        TYPE_REMINDER: '#10b981',
        TYPE_HOLIDAY: '#ef4444',
        TYPE_GOAL: '#3b82f6',
        TYPE_COMPLETED: '#6b7280',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_events'
    )
    title = models.CharField(_('Title'), max_length=200)
    event_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_REMINDER)
    date = models.DateField(_('Date'))
    time = models.TimeField(_('Time'), null=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    is_completed = models.BooleanField(_('Completed'), default=False)
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='calendar_events'
    )
    color = models.CharField(_('Color'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('Calendar Event')
        verbose_name_plural = _('Calendar Events')
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.title} ({self.date})'

    def get_color(self):
        return self.color or self.TYPE_COLORS.get(self.event_type, '#6366f1')
