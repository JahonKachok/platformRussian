from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    path('', views.RoadmapIndexView.as_view(), name='index'),
    path('<slug:slug>/', views.RoadmapView.as_view(), name='course-roadmap'),
]
