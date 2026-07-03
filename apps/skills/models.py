from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class SkillProgress(TimeStampedModel):
    SKILL_READING = 'reading'
    SKILL_LISTENING = 'listening'
    SKILL_SPEAKING = 'speaking'
    SKILL_WRITING = 'writing'
    SKILL_GRAMMAR = 'grammar'
    SKILL_VOCABULARY = 'vocabulary'

    SKILL_CHOICES = [
        (SKILL_READING, _('Reading')),
        (SKILL_LISTENING, _('Listening')),
        (SKILL_SPEAKING, _('Speaking')),
        (SKILL_WRITING, _('Writing')),
        (SKILL_GRAMMAR, _('Grammar')),
        (SKILL_VOCABULARY, _('Vocabulary')),
    ]

    SKILL_COLORS = {
        SKILL_READING: '#6366f1',
        SKILL_LISTENING: '#8b5cf6',
        SKILL_SPEAKING: '#10b981',
        SKILL_WRITING: '#f59e0b',
        SKILL_GRAMMAR: '#3b82f6',
        SKILL_VOCABULARY: '#ec4899',
    }

    SKILL_ICONS = {
        SKILL_READING: '📖',
        SKILL_LISTENING: '🎧',
        SKILL_SPEAKING: '🎤',
        SKILL_WRITING: '✍️',
        SKILL_GRAMMAR: '📝',
        SKILL_VOCABULARY: '💬',
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_progress')
    skill = models.CharField(_('Skill'), max_length=20, choices=SKILL_CHOICES)
    current_score = models.PositiveSmallIntegerField(_('Score (0-100)'), default=0)
    weekly_xp = models.PositiveIntegerField(_('Weekly XP'), default=0)
    monthly_xp = models.PositiveIntegerField(_('Monthly XP'), default=0)
    total_exercises = models.PositiveIntegerField(_('Total Exercises'), default=0)
    streak_days = models.PositiveSmallIntegerField(_('Streak'), default=0)
    last_practiced = models.DateTimeField(_('Last Practiced'), null=True, blank=True)
    last_weekly_reset = models.DateField(null=True, blank=True)
    last_monthly_reset = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('Skill Progress')
        verbose_name_plural = _('Skill Progresses')
        unique_together = ('user', 'skill')

    def __str__(self):
        return f'{self.user} - {self.skill} ({self.current_score}%)'

    @property
    def color(self):
        return self.SKILL_COLORS.get(self.skill, '#6366f1')

    @property
    def icon(self):
        return self.SKILL_ICONS.get(self.skill, '📚')

    @property
    def cefr_label(self):
        s = self.current_score
        if s < 17: return 'A1'
        if s < 34: return 'A2'
        if s < 50: return 'B1'
        if s < 67: return 'B2'
        if s < 84: return 'C1'
        return 'C2'
