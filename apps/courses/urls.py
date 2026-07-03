from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<slug:slug>/enroll/', views.EnrollView.as_view(), name='enroll'),
    path('lesson/<slug:lesson_slug>/', views.LessonView.as_view(), name='lesson'),
    path('lesson/<slug:lesson_slug>/complete/', views.CompleteLessonView.as_view(), name='complete-lesson'),
]
