from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(_('Icon'), max_length=50, default='📚')
    color = models.CharField(_('Color'), max_length=20, default='#6366f1')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    LEVEL_BEGINNER = 'A1'
    LEVEL_ELEMENTARY = 'A2'
    LEVEL_PRE_INT = 'B1'
    LEVEL_INTERMEDIATE = 'B2'
    LEVEL_UPPER = 'C1'
    LEVEL_ADVANCED = 'C2'

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, _('Beginner (A1)')),
        (LEVEL_ELEMENTARY, _('Elementary (A2)')),
        (LEVEL_PRE_INT, _('Pre-Intermediate (B1)')),
        (LEVEL_INTERMEDIATE, _('Intermediate (B2)')),
        (LEVEL_UPPER, _('Upper-Intermediate (C1)')),
        (LEVEL_ADVANCED, _('Advanced (C2)')),
    ]

    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(_('Description'))
    short_description = models.CharField(_('Short description'), max_length=300, blank=True)
    cover = models.ImageField(_('Cover'), upload_to='courses/covers/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='teaching_courses'
    )
    level = models.CharField(_('Level'), max_length=5, choices=LEVEL_CHOICES, default=LEVEL_BEGINNER)
    duration_hours = models.PositiveSmallIntegerField(_('Duration (hours)'), default=10)
    xp_reward = models.PositiveIntegerField(_('XP Reward'), default=500)
    coin_reward = models.PositiveIntegerField(_('Coin Reward'), default=100)
    has_certificate = models.BooleanField(_('Has certificate'), default=True)
    is_published = models.BooleanField(_('Published'), default=False)
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_free = models.BooleanField(_('Free'), default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    @property
    def lesson_count(self):
        return self.lessons.filter(is_published=True).count()

    @property
    def cover_url(self):
        if self.cover:
            return self.cover.url
        return '/static/images/svg/course-default.svg'

    def get_enrollment(self, user):
        try:
            return self.enrollments.get(user=user)
        except Enrollment.DoesNotExist:
            return None


class Lesson(TimeStampedModel):
    TYPE_READING = 'reading'
    TYPE_LISTENING = 'listening'
    TYPE_VOCABULARY = 'vocabulary'
    TYPE_GRAMMAR = 'grammar'
    TYPE_SPEAKING = 'speaking'
    TYPE_WRITING = 'writing'
    TYPE_QUIZ = 'quiz'

    TYPE_CHOICES = [
        (TYPE_READING, _('Reading')),
        (TYPE_LISTENING, _('Listening')),
        (TYPE_VOCABULARY, _('Vocabulary')),
        (TYPE_GRAMMAR, _('Grammar')),
        (TYPE_SPEAKING, _('Speaking')),
        (TYPE_WRITING, _('Writing')),
        (TYPE_QUIZ, _('Quiz')),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField()
    description = models.TextField(_('Description'), blank=True)
    lesson_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_READING)
    content = models.TextField(_('Content'), blank=True)
    audio = models.FileField(_('Audio'), upload_to='lessons/audio/', null=True, blank=True)
    video_url = models.URLField(_('Video URL'), blank=True)
    duration_minutes = models.PositiveSmallIntegerField(_('Duration (minutes)'), default=15)
    xp_reward = models.PositiveIntegerField(_('XP Reward'), default=50)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(_('Published'), default=False)
    is_free_preview = models.BooleanField(_('Free preview'), default=False)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['order']
        unique_together = ('course', 'slug')

    def __str__(self):
        return f'{self.course.title} - {self.title}'

    @property
    def type_icon(self):
        icons = {
            'reading': '📖', 'listening': '🎧', 'vocabulary': '💬',
            'grammar': '📝', 'speaking': '🎤', 'writing': '✍️', 'quiz': '❓'
        }
        return icons.get(self.lesson_type, '📚')


class Enrollment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    progress_percent = models.PositiveSmallIntegerField(default=0)
    completed_lessons = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Enrollment')
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user} enrolled in {self.course}'


class LessonProgress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveSmallIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user} - {self.lesson.title}'
