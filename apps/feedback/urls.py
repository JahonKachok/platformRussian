from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.FeedbackStudentView.as_view(), name='student'),
    path('submit/<slug:lesson_slug>/', views.FeedbackSubmitView.as_view(), name='submit'),
    path('submission/<int:pk>/', views.FeedbackDetailView.as_view(), name='detail'),
    path('teacher/', views.TeacherReviewListView.as_view(), name='teacher-list'),
    path('teacher/<int:pk>/review/', views.TeacherReviewView.as_view(), name='review'),
]
