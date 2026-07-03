from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.JournalListView.as_view(), name='index'),
    path('new/', views.JournalCreateView.as_view(), name='create'),
    path('<int:pk>/', views.JournalEntryView.as_view(), name='entry'),
    path('<int:pk>/delete/', views.JournalDeleteView.as_view(), name='delete'),
]
