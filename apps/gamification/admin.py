from django.contrib import admin
from .models import UserProgress, Achievement, UserAchievement, Badge, LeaderboardEntry


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp', 'level', 'coins', 'streak_days', 'total_lessons_completed')
    search_fields = ('user__email', 'user__first_name')
    ordering = ('-xp',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon', 'xp_reward', 'coin_reward', 'condition_type', 'condition_value')
    list_filter = ('category',)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'required_level')
