from django.contrib import admin
from .models import WordCategory, Word, UserWord


@admin.register(WordCategory)
class WordCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'difficulty', 'part_of_speech', 'translation_uz')
    list_filter = ('difficulty', 'category', 'part_of_speech')
    search_fields = ('word', 'translation_uz', 'definition')
    ordering = ['order', 'word']
