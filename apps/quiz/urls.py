from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.QuizListView.as_view(), name='list'),
    path('<int:pk>/', views.QuizStartView.as_view(), name='start'),
    path('attempt/<int:attempt_id>/q/<int:question_num>/', views.QuizQuestionView.as_view(), name='question'),
    path('attempt/<int:attempt_id>/submit/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('attempt/<int:attempt_id>/complete/', views.QuizCompleteView.as_view(), name='complete'),
    path('attempt/<int:attempt_id>/results/', views.QuizResultsView.as_view(), name='results'),
]
