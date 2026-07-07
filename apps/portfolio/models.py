from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Portfolio(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio'
    )
    bio = models.TextField(_('Professional Bio'), blank=True)
    skills_summary = models.TextField(_('Skills Summary'), blank=True)
    goals = models.TextField(_('Learning Goals'), blank=True)
    is_public = models.BooleanField(_('Public'), default=False)

    class Meta:
        verbose_name = _('Portfolio')
        verbose_name_plural = _('Portfolios')

    def __str__(self):
        return f'{self.user} Portfolio'


class PortfolioItem(TimeStampedModel):
    TYPE_WRITING = 'writing'
    TYPE_SPEAKING = 'speaking'
    TYPE_PROJECT = 'project'
    TYPE_HOMEWORK = 'homework'
    TYPE_ACHIEVEMENT = 'achievement'

    TYPE_CHOICES = [
        (TYPE_WRITING, _('Writing Task')),
        (TYPE_SPEAKING, _('Speaking Record')),
        (TYPE_PROJECT, _('Project')),
        (TYPE_HOMEWORK, _('Homework')),
        (TYPE_ACHIEVEMENT, _('Achievement')),
    ]

    TYPE_ICONS = {
        TYPE_WRITING: '✍️',
        TYPE_SPEAKING: '🎤',
        TYPE_PROJECT: '📁',
        TYPE_HOMEWORK: '📝',
        TYPE_ACHIEVEMENT: '🏆',
    }

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    file = models.FileField(_('File'), upload_to='portfolio/', null=True, blank=True)
    score = models.DecimalField(_('Score'), max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_feedback = models.TextField(_('Teacher Feedback'), blank=True)
    rating = models.PositiveSmallIntegerField(
        _('Admin Rating'), null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5 stars'),
    )
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='rated_portfolio_items',
        verbose_name=_('Rated By'),
    )
    rated_at = models.DateTimeField(_('Rated At'), null=True, blank=True)
    date = models.DateField(_('Date'), auto_now_add=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Portfolio Item')
        verbose_name_plural = _('Portfolio Items')
        ordering = ['-date']

    def __str__(self):
        return f'{self.portfolio.user} - {self.title}'

    @property
    def type_icon(self):
        return self.TYPE_ICONS.get(self.item_type, '📄')

    @property
    def stars_display(self):
        if self.rating:
            return '★' * self.rating + '☆' * (5 - self.rating)
        return ''
