from django.urls import path
from . import views

app_name = 'study_calendar'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='index'),
    path('event/create/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/toggle/', views.EventToggleView.as_view(), name='event-toggle'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
]
