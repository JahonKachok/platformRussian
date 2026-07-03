from django.contrib import admin
from .models import SkillProgress

@admin.register(SkillProgress)
class SkillProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'current_score', 'weekly_xp', 'total_exercises')
    list_filter = ('skill',)
    search_fields = ('user__email',)
