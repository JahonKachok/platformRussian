from django.contrib import admin
from .models import ForumTopic, ForumReply

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'is_pinned', 'views')
    list_filter = ('is_pinned', 'is_locked', 'is_announcement')
    search_fields = ('title', 'author__email')

@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'is_solution', 'created_at')
