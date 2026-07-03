from django.urls import path
from . import views

app_name = 'learning_path'

urlpatterns = [
    path('', views.LearningPathView.as_view(), name='index'),
    path('item/<int:pk>/complete/', views.LearningPathCompleteView.as_view(), name='complete'),
    path('refresh/', views.LearningPathRefreshView.as_view(), name='refresh'),
]
