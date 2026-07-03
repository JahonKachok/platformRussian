from django.contrib import admin
from .models import HomeworkSubmission, TeacherFeedback

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email',)

@admin.register(TeacherFeedback)
class TeacherFeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'teacher', 'score')
