from django.contrib import admin
from .models import JournalEntry

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood', 'self_rating')
    list_filter = ('mood', 'self_rating')
    search_fields = ('user__email',)
