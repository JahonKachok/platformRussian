from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse
from .models import GrammarTopic, GrammarExercise, UserGrammarProgress
import json


class GrammarTopicsView(LoginRequiredMixin, ListView):
    model = GrammarTopic
    template_name = 'grammar/topics.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return GrammarTopic.objects.filter(is_published=True).order_by('order', 'level')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_progress = {
            up.topic_id: up
            for up in UserGrammarProgress.objects.filter(user=self.request.user)
        }
        ctx['user_progress'] = user_progress
        ctx['levels'] = GrammarTopic.LEVEL_CHOICES
        return ctx


class GrammarTopicDetailView(LoginRequiredMixin, DetailView):
    model = GrammarTopic
    template_name = 'grammar/detail.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return GrammarTopic.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topic = self.object
        ctx['examples'] = topic.grammar_examples.all()
        ctx['exercises'] = topic.exercises.all()

        try:
            ctx['user_progress'] = UserGrammarProgress.objects.get(
                user=self.request.user, topic=topic
            )
        except UserGrammarProgress.DoesNotExist:
            ctx['user_progress'] = None

        return ctx


class CheckExerciseView(LoginRequiredMixin, View):
    def post(self, request, exercise_id):
        exercise = GrammarExercise.objects.get(pk=exercise_id)
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip().lower()
        correct = exercise.correct_answer.strip().lower()

        is_correct = user_answer == correct
        progress, _ = UserGrammarProgress.objects.get_or_create(
            user=request.user, topic=exercise.topic
        )
        progress.exercises_completed += 1
        if is_correct:
            progress.correct_answers += 1
        progress.save()

        return JsonResponse({
            'is_correct': is_correct,
            'correct_answer': exercise.correct_answer,
            'explanation': exercise.explanation,
        })
