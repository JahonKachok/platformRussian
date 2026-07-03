from django.urls import path
from . import views

app_name = 'grammar'

urlpatterns = [
    path('', views.GrammarTopicsView.as_view(), name='topics'),
    path('<slug:slug>/', views.GrammarTopicDetailView.as_view(), name='topic-detail'),
    path('exercise/<int:exercise_id>/check/', views.CheckExerciseView.as_view(), name='check-exercise'),
]
