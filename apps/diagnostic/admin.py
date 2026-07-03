from django.contrib import admin
from .models import DiagnosticTest, DiagnosticQuestion, DiagnosticAttempt

class DiagnosticQuestionInline(admin.TabularInline):
    model = DiagnosticQuestion
    extra = 1

@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'test_type', 'time_limit_minutes', 'is_active')
    list_filter = ('test_type', 'is_active')
    inlines = [DiagnosticQuestionInline]

@admin.register(DiagnosticAttempt)
class DiagnosticAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'percentage', 'cefr_level', 'completed')
