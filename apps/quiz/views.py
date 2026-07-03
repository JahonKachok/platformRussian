from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView, ListView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json
import random

from .models import Quiz, Question, Choice, QuizAttempt, UserAnswer


class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quiz/list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quiz.objects.filter(is_published=True).order_by('-created_at')


class QuizStartView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz/start.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        quiz = self.object
        ctx['question_count'] = quiz.questions.count()
        ctx['best_attempt'] = QuizAttempt.objects.filter(
            user=self.request.user, quiz=quiz, completed=True
        ).order_by('-percentage').first()
        return ctx

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)
        return redirect('quiz:question', attempt_id=attempt.id, question_num=1)


class QuizQuestionView(LoginRequiredMixin, TemplateView):
    template_name = 'quiz/question.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = get_object_or_404(QuizAttempt, pk=kwargs['attempt_id'], user=self.request.user)
        questions = list(attempt.quiz.questions.prefetch_related('choices').order_by('order'))

        if attempt.quiz.shuffle_questions and not attempt.answers.exists():
            random.shuffle(questions)

        q_num = kwargs['question_num']
        if q_num < 1 or q_num > len(questions):
            return ctx

        question = questions[q_num - 1]
        ctx['attempt'] = attempt
        ctx['quiz'] = attempt.quiz
        ctx['question'] = question
        ctx['question_num'] = q_num
        ctx['total_questions'] = len(questions)
        ctx['progress_percent'] = int(((q_num - 1) / len(questions)) * 100)
        ctx['choices'] = question.choices.all()
        ctx['time_limit'] = attempt.quiz.time_limit_minutes * 60
        return ctx


class SubmitAnswerView(LoginRequiredMixin, View):
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
        data = json.loads(request.body)
        question_id = data.get('question_id')
        choice_id = data.get('choice_id')
        text_answer = data.get('text_answer', '')

        question = get_object_or_404(Question, pk=question_id)

        is_correct = False
        points_earned = 0
        selected_choice = None

        if choice_id:
            selected_choice = get_object_or_404(Choice, pk=choice_id, question=question)
            is_correct = selected_choice.is_correct
        elif text_answer:
            correct = question.choices.filter(is_correct=True).first()
            is_correct = correct and text_answer.strip().lower() == correct.text.strip().lower()

        if is_correct:
            points_earned = question.points

        UserAnswer.objects.update_or_create(
            attempt=attempt, question=question,
            defaults={
                'selected_choice': selected_choice,
                'text_answer': text_answer,
                'is_correct': is_correct,
                'points_earned': points_earned,
            }
        )

        correct_choice = question.choices.filter(is_correct=True).first()
        return JsonResponse({
            'is_correct': is_correct,
            'correct_choice_id': correct_choice.id if correct_choice else None,
            'explanation': question.explanation,
            'points': points_earned,
        })


class QuizCompleteView(LoginRequiredMixin, View):
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
        if attempt.completed:
            return redirect('quiz:results', attempt_id=attempt_id)

        answers = attempt.answers.all()
        score = sum(a.points_earned for a in answers)
        max_score = sum(q.points for q in attempt.quiz.questions.all())
        percentage = int((score / max_score) * 100) if max_score else 0
        passed = percentage >= attempt.quiz.pass_score

        attempt.score = score
        attempt.max_score = max_score
        attempt.percentage = percentage
        attempt.passed = passed
        attempt.completed = True
        attempt.completed_at = timezone.now()

        xp_earned = attempt.quiz.xp_reward if passed else attempt.quiz.xp_reward // 2
        attempt.xp_earned = xp_earned
        attempt.save()

        if passed:
            try:
                from apps.gamification.models import UserProgress
                up = UserProgress.objects.get(user=request.user)
                up.add_xp(xp_earned, 'quiz_complete')
                up.total_quizzes_completed += 1
                up.save(update_fields=['total_quizzes_completed'])
            except Exception:
                pass

        return redirect('quiz:results', attempt_id=attempt_id)


class QuizResultsView(LoginRequiredMixin, DetailView):
    model = QuizAttempt
    template_name = 'quiz/results.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = self.object
        ctx['answers'] = attempt.answers.select_related('question', 'selected_choice').all()
        ctx['correct_count'] = attempt.answers.filter(is_correct=True).count()
        ctx['incorrect_count'] = attempt.answers.filter(is_correct=False).count()
        return ctx
