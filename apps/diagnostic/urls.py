from django.urls import path
from . import views

app_name = 'diagnostic'

urlpatterns = [
    path('', views.DiagnosticIndexView.as_view(), name='index'),
    path('test/<int:pk>/start/', views.DiagnosticStartView.as_view(), name='start'),
    path('attempt/<int:attempt_id>/q/<int:q_num>/', views.DiagnosticQuestionView.as_view(), name='question'),
    path('attempt/<int:attempt_id>/submit/', views.DiagnosticSubmitView.as_view(), name='submit'),
    path('attempt/<int:attempt_id>/complete/', views.DiagnosticCompleteView.as_view(), name='complete'),
    path('attempt/<int:attempt_id>/results/', views.DiagnosticResultsView.as_view(), name='results'),
]
