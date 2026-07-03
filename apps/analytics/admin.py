from django.contrib import admin
from .models import StudySession

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'minutes_studied', 'xp_earned', 'lessons_completed')
    list_filter = ('date',)
    search_fields = ('user__email',)
