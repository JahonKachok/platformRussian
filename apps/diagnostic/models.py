from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class DiagnosticTest(TimeStampedModel):
    TYPE_PLACEMENT = 'placement'
    TYPE_GRAMMAR = 'grammar'
    TYPE_VOCABULARY = 'vocabulary'
    TYPE_READING = 'reading'
    TYPE_LISTENING = 'listening'
    TYPE_WRITING = 'writing'

    TYPE_CHOICES = [
        (TYPE_PLACEMENT, _('Placement Test')),
        (TYPE_GRAMMAR, _('Grammar Test')),
        (TYPE_VOCABULARY, _('Vocabulary Test')),
        (TYPE_READING, _('Reading Level')),
        (TYPE_LISTENING, _('Listening Level')),
        (TYPE_WRITING, _('Writing Level')),
    ]

    title = models.CharField(_('Title'), max_length=200)
    test_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    time_limit_minutes = models.PositiveSmallIntegerField(_('Time Limit (min)'), default=30)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Diagnostic Test')
        verbose_name_plural = _('Diagnostic Tests')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class DiagnosticQuestion(TimeStampedModel):
    QT_MULTIPLE = 'multiple'
    QT_TEXT = 'text'
    QT_TRUE_FALSE = 'true_false'

    QT_CHOICES = [
        (QT_MULTIPLE, _('Multiple Choice')),
        (QT_TEXT, _('Text Answer')),
        (QT_TRUE_FALSE, _('True / False')),
    ]

    CEFR_CHOICES = [
        ('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'),
        ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2'),
    ]

    test = models.ForeignKey(DiagnosticTest, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(_('Question'))
    question_type = models.CharField(_('Type'), max_length=20, choices=QT_CHOICES, default=QT_MULTIPLE)
    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)
    correct_answer = models.CharField(_('Correct Answer'), max_length=300)
    explanation = models.TextField(_('Explanation'), blank=True)
    cefr_level = models.CharField(_('CEFR Level'), max_length=2, choices=CEFR_CHOICES, default='A1')
    points = models.PositiveSmallIntegerField(_('Points'), default=1)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def get_options(self):
        opts = []
        for label, val in [('A', self.option_a), ('B', self.option_b),
                           ('C', self.option_c), ('D', self.option_d)]:
            if val:
                opts.append((label, val))
        return opts


class DiagnosticAttempt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnostic_attempts')
    test = models.ForeignKey(DiagnosticTest, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    percentage = models.PositiveSmallIntegerField(default=0)
    cefr_level = models.CharField(_('CEFR Level'), max_length=2, blank=True)
    recommendation = models.TextField(_('Recommendation'), blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.test.title}'


class DiagnosticAnswer(TimeStampedModel):
    attempt = models.ForeignKey(DiagnosticAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(DiagnosticQuestion, on_delete=models.CASCADE)
    given_answer = models.CharField(max_length=300, blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')
