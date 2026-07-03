from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from .models import UserProgress, Achievement, UserAchievement, LeaderboardEntry


class LeaderboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gamification/leaderboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        period = self.request.GET.get('period', 'weekly')

        top_users = UserProgress.objects.select_related('user').order_by('-xp')[:50]
        ctx['leaderboard'] = top_users
        ctx['period'] = period

        try:
            user_progress = UserProgress.objects.get(user=self.request.user)
            all_users = list(UserProgress.objects.order_by('-xp').values_list('user_id', flat=True))
            user_rank = all_users.index(self.request.user.id) + 1
            ctx['user_progress'] = user_progress
            ctx['user_rank'] = user_rank
        except (UserProgress.DoesNotExist, ValueError):
            ctx['user_progress'] = None
            ctx['user_rank'] = '-'

        return ctx


class AchievementsView(LoginRequiredMixin, TemplateView):
    template_name = 'gamification/achievements.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        all_achievements = Achievement.objects.all()
        earned_ids = set(
            UserAchievement.objects.filter(user=self.request.user).values_list('achievement_id', flat=True)
        )
        ctx['achievements'] = all_achievements
        ctx['earned_ids'] = earned_ids
        ctx['earned_count'] = len(earned_ids)
        ctx['total_count'] = all_achievements.count()
        return ctx
