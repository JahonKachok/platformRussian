from django.contrib import admin
from .models import GrammarTopic, GrammarExample, GrammarExercise


class ExampleInline(admin.TabularInline):
    model = GrammarExample
    extra = 2


class ExerciseInline(admin.TabularInline):
    model = GrammarExercise
    extra = 2


@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'order', 'is_published')
    list_filter = ('level', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ExampleInline, ExerciseInline]
