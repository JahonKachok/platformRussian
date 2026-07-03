from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark-read/', views.MarkReadView.as_view(), name='mark-all-read'),
    path('<int:pk>/mark-read/', views.MarkReadView.as_view(), name='mark-read'),
    path('count/', views.NotificationCountView.as_view(), name='count'),
]
