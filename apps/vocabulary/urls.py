from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [
    path('', views.FlashcardsView.as_view(), name='flashcards'),
    path('list/', views.VocabularyListView.as_view(), name='list'),
    path('word/<int:word_id>/status/', views.WordStatusView.as_view(), name='word-status'),
]
