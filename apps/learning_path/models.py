from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class LearningPathItem(TimeStampedModel):
    TYPE_LESSON = 'lesson'
    TYPE_QUIZ = 'quiz'
    TYPE_GRAMMAR = 'grammar'
    TYPE_VOCABULARY = 'vocabulary'
    TYPE_DIAGNOSTIC = 'diagnostic'
    TYPE_REVIEW = 'review'

    TYPE_CHOICES = [
        (TYPE_LESSON, _('Lesson')),
        (TYPE_QUIZ, _('Quiz')),
        (TYPE_GRAMMAR, _('Grammar Topic')),
        (TYPE_VOCABULARY, _('Vocabulary Practice')),
        (TYPE_DIAGNOSTIC, _('Diagnostic Test')),
        (TYPE_REVIEW, _('Review Session')),
    ]

    TYPE_ICONS = {
        TYPE_LESSON: '📖', TYPE_QUIZ: '❓',
        TYPE_GRAMMAR: '📝', TYPE_VOCABULARY: '💬',
        TYPE_DIAGNOSTIC: '🔬', TYPE_REVIEW: '🔄',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_path_items'
    )
    content_type = models.CharField(_('Content Type'), max_length=20, choices=TYPE_CHOICES)
    content_id = models.PositiveIntegerField(_('Content ID'), null=True, blank=True)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    reason = models.TextField(_('Why This?'), blank=True)
    priority = models.PositiveSmallIntegerField(_('Priority'), default=0)
    estimated_minutes = models.PositiveSmallIntegerField(_('Estimated Time (min)'), default=15)
    is_completed = models.BooleanField(_('Completed'), default=False)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Learning Path Item')
        verbose_name_plural = _('Learning Path Items')
        ordering = ['is_completed', 'priority']

    def __str__(self):
        return f'{self.user} - {self.title}'

    @property
    def type_icon(self):
        return self.TYPE_ICONS.get(self.content_type, '📚')
