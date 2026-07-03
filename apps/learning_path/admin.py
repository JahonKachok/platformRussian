from django.contrib import admin
from .models import LearningPathItem

@admin.register(LearningPathItem)
class LearningPathItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'content_type', 'priority', 'is_completed')
    list_filter = ('content_type', 'is_completed')
    search_fields = ('user__email', 'title')
