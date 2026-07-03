from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class HomeworkSubmission(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending Review')),
        (STATUS_REVIEWED, _('Reviewed')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='homework_submissions'
    )
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.CASCADE, related_name='homework_submissions'
    )
    text = models.TextField(_('Written Answer'), blank=True)
    file = models.FileField(_('File'), upload_to='homework/files/', null=True, blank=True)
    audio = models.FileField(_('Audio Recording'), upload_to='homework/audio/', null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        verbose_name = _('Homework Submission')
        verbose_name_plural = _('Homework Submissions')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.lesson.title}'


class TeacherFeedback(TimeStampedModel):
    submission = models.OneToOneField(
        HomeworkSubmission, on_delete=models.CASCADE, related_name='feedback'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_feedbacks'
    )
    text_feedback = models.TextField(_('Text Feedback'))
    audio_feedback = models.FileField(_('Audio Feedback'), upload_to='feedback/audio/', null=True, blank=True)
    score = models.DecimalField(_('Score'), max_digits=5, decimal_places=2, null=True, blank=True)
    grammar_score = models.PositiveSmallIntegerField(_('Grammar (0-100)'), default=0)
    vocabulary_score = models.PositiveSmallIntegerField(_('Vocabulary (0-100)'), default=0)
    fluency_score = models.PositiveSmallIntegerField(_('Fluency (0-100)'), default=0)
    content_score = models.PositiveSmallIntegerField(_('Content (0-100)'), default=0)

    class Meta:
        verbose_name = _('Teacher Feedback')
        verbose_name_plural = _('Teacher Feedbacks')

    def __str__(self):
        return f'Feedback for {self.submission}'

    @property
    def average_score(self):
        scores = [self.grammar_score, self.vocabulary_score, self.fluency_score, self.content_score]
        valid = [s for s in scores if s > 0]
        return sum(valid) // len(valid) if valid else 0
