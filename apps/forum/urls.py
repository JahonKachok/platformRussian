from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.ForumIndexView.as_view(), name='index'),
    path('course/<slug:slug>/', views.ForumCourseView.as_view(), name='course'),
    path('topic/<int:pk>/', views.ForumTopicView.as_view(), name='topic'),
    path('course/<slug:slug>/create/', views.ForumTopicCreateView.as_view(), name='topic-create'),
    path('reply/<int:topic_id>/', views.ForumReplyCreateView.as_view(), name='reply-create'),
    path('like/', views.ForumLikeView.as_view(), name='like'),
]
