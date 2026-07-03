from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.core.utils import calculate_level


class UserProgress(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='progress', verbose_name=_('User')
    )
    xp = models.PositiveIntegerField(_('XP'), default=0)
    level = models.PositiveSmallIntegerField(_('Level'), default=1)
    coins = models.PositiveIntegerField(_('Coins'), default=0)
    streak_days = models.PositiveSmallIntegerField(_('Streak days'), default=0)
    longest_streak = models.PositiveSmallIntegerField(_('Longest streak'), default=0)
    last_activity_date = models.DateField(_('Last activity date'), null=True, blank=True)
    total_lessons_completed = models.PositiveIntegerField(default=0)
    total_quizzes_completed = models.PositiveIntegerField(default=0)
    total_words_learned = models.PositiveIntegerField(default=0)
    daily_xp = models.PositiveIntegerField(_('Daily XP'), default=0)
    daily_goal = models.PositiveIntegerField(_('Daily goal XP'), default=100)
    last_daily_reset = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('User Progress')
        verbose_name_plural = _('User Progresses')

    def __str__(self):
        return f'{self.user} - Level {self.level} ({self.xp} XP)'

    def add_xp(self, amount, reason=''):
        self.xp += amount
        self.daily_xp += amount
        new_level = calculate_level(self.xp)
        leveled_up = new_level > self.level
        self.level = new_level
        self.save(update_fields=['xp', 'level', 'daily_xp'])
        return leveled_up

    def add_coins(self, amount):
        self.coins += amount
        self.save(update_fields=['coins'])

    @property
    def level_progress_percent(self):
        from apps.core.utils import get_level_progress
        return get_level_progress(self.xp)

    @property
    def daily_goal_percent(self):
        if self.daily_goal == 0:
            return 100
        return min(int((self.daily_xp / self.daily_goal) * 100), 100)


class Achievement(TimeStampedModel):
    CATEGORY_LEARNING = 'learning'
    CATEGORY_STREAK = 'streak'
    CATEGORY_SOCIAL = 'social'
    CATEGORY_MILESTONE = 'milestone'

    CATEGORY_CHOICES = [
        (CATEGORY_LEARNING, _('Learning')),
        (CATEGORY_STREAK, _('Streak')),
        (CATEGORY_SOCIAL, _('Social')),
        (CATEGORY_MILESTONE, _('Milestone')),
    ]

    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    icon = models.CharField(_('Icon'), max_length=100, default='🏆')
    category = models.CharField(_('Category'), max_length=20, choices=CATEGORY_CHOICES)
    xp_reward = models.PositiveIntegerField(_('XP Reward'), default=50)
    coin_reward = models.PositiveIntegerField(_('Coin Reward'), default=10)
    condition_type = models.CharField(_('Condition type'), max_length=50)
    condition_value = models.PositiveIntegerField(_('Condition value'), default=1)
    is_hidden = models.BooleanField(_('Hidden'), default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Achievement')
        verbose_name_plural = _('Achievements')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class UserAchievement(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='achievements_earned'
    )
    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE,
        related_name='userachievement'
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('User Achievement')
        unique_together = ('user', 'achievement')


class Badge(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    image = models.ImageField(_('Image'), upload_to='badges/', null=True, blank=True)
    icon = models.CharField(_('Icon'), max_length=50, default='🥇')
    color = models.CharField(_('Color'), max_length=20, default='gold')
    required_level = models.PositiveSmallIntegerField(_('Required level'), default=1)

    class Meta:
        verbose_name = _('Badge')
        verbose_name_plural = _('Badges')

    def __str__(self):
        return self.name


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')


class LeaderboardEntry(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    period = models.CharField(_('Period'), max_length=20, default='weekly')
    xp = models.PositiveIntegerField(default=0)
    rank = models.PositiveSmallIntegerField(default=0)
    week = models.PositiveSmallIntegerField(null=True, blank=True)
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['rank']


class DailyChallenge(TimeStampedModel):
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=20)
    date = models.DateField(_('Date'))
    challenge_type = models.CharField(max_length=50, default='quiz')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Daily Challenge')
        ordering = ['-date']

    def __str__(self):
        return f'{self.title} ({self.date})'


class UserDailyChallenge(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')
