from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsIndexView.as_view(), name='index'),
    path('progress.pdf', views.ProgressReportPDFView.as_view(), name='progress-pdf'),
    path('quiz.pdf', views.QuizReportPDFView.as_view(), name='quiz-pdf'),
    path('admin/', views.AdminAnalyticsView.as_view(), name='admin-analytics'),
]
