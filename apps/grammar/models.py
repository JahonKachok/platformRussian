from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class GrammarTopic(TimeStampedModel):
    LEVEL_CHOICES = [
        ('A1', 'A1 - Beginner'), ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Pre-Intermediate'), ('B2', 'B2 - Intermediate'),
        ('C1', 'C1 - Upper'), ('C2', 'C2 - Advanced'),
    ]

    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(unique=True)
    level = models.CharField(_('Level'), max_length=5, choices=LEVEL_CHOICES, default='A1')
    explanation = models.TextField(_('Explanation'))
    examples = models.TextField(_('Examples'), blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    icon = models.CharField(_('Icon'), max_length=10, default='📝')
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Grammar Topic')
        verbose_name_plural = _('Grammar Topics')
        ordering = ['order', 'level', 'title']

    def __str__(self):
        return f'{self.level} - {self.title}'


class GrammarExample(TimeStampedModel):
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='grammar_examples')
    sentence = models.CharField(_('English sentence'), max_length=500)
    translation = models.CharField(_('Translation'), max_length=500)
    explanation = models.CharField(_('Short explanation'), max_length=300, blank=True)
    is_correct = models.BooleanField(_('Correct form'), default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.sentence


class GrammarExercise(TimeStampedModel):
    TYPE_FILL_BLANK = 'fill_blank'
    TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    TYPE_REORDER = 'reorder'
    TYPE_TRANSFORM = 'transform'

    TYPE_CHOICES = [
        (TYPE_FILL_BLANK, _('Fill in the blank')),
        (TYPE_MULTIPLE_CHOICE, _('Multiple choice')),
        (TYPE_REORDER, _('Reorder words')),
        (TYPE_TRANSFORM, _('Transform sentence')),
    ]

    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES)
    question = models.TextField(_('Question'))
    options = models.JSONField(_('Options'), default=list, blank=True)
    correct_answer = models.TextField(_('Correct answer'))
    explanation = models.TextField(_('Explanation'), blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.topic.title} - Exercise {self.order}'


class UserGrammarProgress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE)
    exercises_completed = models.PositiveSmallIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'topic')
