from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class WordCategory(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📝')
    color = models.CharField(max_length=20, default='#6366f1')

    class Meta:
        verbose_name_plural = _('Word Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class Word(TimeStampedModel):
    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_MEDIUM = 'medium'
    DIFFICULTY_HARD = 'hard'

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, _('Easy')),
        (DIFFICULTY_MEDIUM, _('Medium')),
        (DIFFICULTY_HARD, _('Hard')),
    ]

    word = models.CharField(_('Word'), max_length=100)
    pronunciation = models.CharField(_('Pronunciation (IPA)'), max_length=200, blank=True)
    audio = models.FileField(_('Audio'), upload_to='vocabulary/audio/', null=True, blank=True)
    translation_uz = models.CharField(_('Translation (Uzbek)'), max_length=300)
    translation_ru = models.CharField(_('Translation (Russian)'), max_length=300, blank=True)
    definition = models.TextField(_('Definition'), blank=True)
    example_sentence = models.TextField(_('Example sentence'), blank=True)
    example_translation = models.TextField(_('Example translation'), blank=True)
    image = models.ImageField(_('Image'), upload_to='vocabulary/images/', null=True, blank=True)
    synonyms = models.TextField(_('Synonyms'), blank=True)
    antonyms = models.TextField(_('Antonyms'), blank=True)
    category = models.ForeignKey(WordCategory, on_delete=models.SET_NULL, null=True, related_name='words')
    difficulty = models.CharField(_('Difficulty'), max_length=10, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_EASY)
    part_of_speech = models.CharField(_('Part of speech'), max_length=50, blank=True)
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary'
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Word')
        verbose_name_plural = _('Words')
        ordering = ['order', 'word']

    def __str__(self):
        return self.word

    @property
    def synonym_list(self):
        return [s.strip() for s in self.synonyms.split(',') if s.strip()]

    @property
    def antonym_list(self):
        return [a.strip() for a in self.antonyms.split(',') if a.strip()]


class UserWord(TimeStampedModel):
    STATUS_NEW = 'new'
    STATUS_LEARNING = 'learning'
    STATUS_MASTERED = 'mastered'

    STATUS_CHOICES = [
        (STATUS_NEW, _('New')),
        (STATUS_LEARNING, _('Learning')),
        (STATUS_MASTERED, _('Mastered')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='user_data')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    is_favorite = models.BooleanField(_('Favorite'), default=False)
    correct_count = models.PositiveSmallIntegerField(default=0)
    incorrect_count = models.PositiveSmallIntegerField(default=0)
    next_review = models.DateTimeField(null=True, blank=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'word')
        verbose_name = _('User Word')

    def __str__(self):
        return f'{self.user} - {self.word}'

    @property
    def accuracy(self):
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0
        return int((self.correct_count / total) * 100)
