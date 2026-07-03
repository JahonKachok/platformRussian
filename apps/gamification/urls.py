from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
]
