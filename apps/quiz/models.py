from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Quiz(TimeStampedModel):
    TYPE_GENERAL = 'general'
    TYPE_LESSON = 'lesson'
    TYPE_COURSE = 'course'
    TYPE_DAILY = 'daily'

    TYPE_CHOICES = [
        (TYPE_GENERAL, _('General')),
        (TYPE_LESSON, _('Lesson Quiz')),
        (TYPE_COURSE, _('Course Quiz')),
        (TYPE_DAILY, _('Daily Challenge')),
    ]

    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    quiz_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_GENERAL)
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes'
    )
    time_limit_minutes = models.PositiveSmallIntegerField(_('Time limit (minutes)'), default=15)
    pass_score = models.PositiveSmallIntegerField(_('Pass score (%)'), default=70)
    xp_reward = models.PositiveIntegerField(_('XP Reward'), default=100)
    coin_reward = models.PositiveIntegerField(_('Coin Reward'), default=20)
    is_published = models.BooleanField(_('Published'), default=True)
    shuffle_questions = models.BooleanField(_('Shuffle questions'), default=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()


class Question(TimeStampedModel):
    TYPE_MCQ = 'mcq'
    TYPE_TRUE_FALSE = 'true_false'
    TYPE_FILL_BLANK = 'fill_blank'
    TYPE_MATCHING = 'matching'

    TYPE_CHOICES = [
        (TYPE_MCQ, _('Multiple Choice')),
        (TYPE_TRUE_FALSE, _('True/False')),
        (TYPE_FILL_BLANK, _('Fill in the blank')),
        (TYPE_MATCHING, _('Matching')),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_MCQ)
    text = models.TextField(_('Question text'))
    image = models.ImageField(_('Image'), upload_to='quiz/questions/', null=True, blank=True)
    audio = models.FileField(_('Audio'), upload_to='quiz/audio/', null=True, blank=True)
    explanation = models.TextField(_('Explanation'), blank=True)
    points = models.PositiveSmallIntegerField(_('Points'), default=10)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.quiz.title} - Q{self.order}'


class Choice(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(_('Choice text'), max_length=500)
    is_correct = models.BooleanField(_('Correct'), default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class QuizAttempt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveSmallIntegerField(default=0)
    max_score = models.PositiveSmallIntegerField(default=0)
    percentage = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    xp_earned = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.quiz.title} ({self.percentage}%)'


class UserAnswer(TimeStampedModel):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')
