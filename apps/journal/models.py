from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class JournalEntry(TimeStampedModel):
    MOOD_GREAT = 'great'
    MOOD_GOOD = 'good'
    MOOD_NEUTRAL = 'neutral'
    MOOD_TIRED = 'tired'
    MOOD_FRUSTRATED = 'frustrated'

    MOOD_CHOICES = [
        (MOOD_GREAT, _('Great 😄')),
        (MOOD_GOOD, _('Good 🙂')),
        (MOOD_NEUTRAL, _('Neutral 😐')),
        (MOOD_TIRED, _('Tired 😴')),
        (MOOD_FRUSTRATED, _('Frustrated 😤')),
    ]

    MOOD_EMOJIS = {
        MOOD_GREAT: '😄', MOOD_GOOD: '🙂', MOOD_NEUTRAL: '😐',
        MOOD_TIRED: '😴', MOOD_FRUSTRATED: '😤',
    }

    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries'
    )
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries'
    )
    date = models.DateField(_('Date'), auto_now_add=True)
    what_learned = models.TextField(_('What did you learn today?'))
    what_was_difficult = models.TextField(_('What was difficult?'), blank=True)
    topics_to_revisit = models.TextField(_('Topics to revisit'), blank=True)
    self_rating = models.PositiveSmallIntegerField(_('Self Rating'), choices=RATING_CHOICES, default=3)
    mood = models.CharField(_('Mood'), max_length=15, choices=MOOD_CHOICES, default=MOOD_NEUTRAL)

    class Meta:
        verbose_name = _('Journal Entry')
        verbose_name_plural = _('Journal Entries')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.user} Journal - {self.date}'

    @property
    def mood_emoji(self):
        return self.MOOD_EMOJIS.get(self.mood, '😐')
