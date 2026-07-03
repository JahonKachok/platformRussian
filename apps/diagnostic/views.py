from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
import json

from .models import DiagnosticTest, DiagnosticQuestion, DiagnosticAttempt, DiagnosticAnswer

CEFR_THRESHOLDS = [
    (0, 16, 'A1'), (17, 33, 'A2'), (34, 49, 'B1'),
    (50, 66, 'B2'), (67, 83, 'C1'), (84, 100, 'C2'),
]

CEFR_COURSE_LEVELS = {
    'A1': 'A1', 'A2': 'A2', 'B1': 'B1', 'B2': 'B2', 'C1': 'C1', 'C2': 'C2',
}

RECOMMENDATIONS = {
    'A1': 'Start with basic English for Beginners. Focus on everyday vocabulary and simple sentences.',
    'A2': 'Elementary level is right for you. Practice basic grammar and common phrases.',
    'B1': 'Pre-Intermediate suits you well. Focus on tense variety, reading, and structured writing.',
    'B2': 'Intermediate level. Work on complex grammar, essay writing, and advanced listening.',
    'C1': 'Upper-Intermediate/Advanced. Focus on academic vocabulary, debate skills, and nuanced writing.',
    'C2': 'Proficient level. Tackle native-level texts, presentations, and professional writing.',
}


def score_to_cefr(percentage):
    for lo, hi, level in CEFR_THRESHOLDS:
        if lo <= percentage <= hi:
            return level
    return 'A1'


class DiagnosticIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'diagnostic/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tests = DiagnosticTest.objects.filter(is_active=True).order_by('order')
        user_attempts = {
            a.test_id: a for a in
            DiagnosticAttempt.objects.filter(user=self.request.user, completed=True).order_by('-completed_at')
        }
        ctx['tests'] = tests
        ctx['user_attempts'] = user_attempts
        # Latest overall result
        latest = DiagnosticAttempt.objects.filter(
            user=self.request.user, completed=True, test__test_type='placement'
        ).order_by('-completed_at').first()
        ctx['latest_result'] = latest
        return ctx


class DiagnosticStartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        test = get_object_or_404(DiagnosticTest, pk=pk, is_active=True)
        attempt = DiagnosticAttempt.objects.create(user=request.user, test=test)
        return redirect('diagnostic:question', attempt_id=attempt.id, q_num=1)


class DiagnosticQuestionView(LoginRequiredMixin, TemplateView):
    template_name = 'diagnostic/question.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = get_object_or_404(DiagnosticAttempt, pk=kwargs['attempt_id'], user=self.request.user)
        questions = list(attempt.test.questions.order_by('order'))
        q_num = kwargs['q_num']
        if q_num < 1 or q_num > len(questions):
            return ctx
        question = questions[q_num - 1]
        ctx.update({
            'attempt': attempt, 'question': question,
            'q_num': q_num, 'total': len(questions),
            'progress_percent': int(((q_num - 1) / len(questions)) * 100),
            'options': question.get_options(),
            'time_limit': attempt.test.time_limit_minutes * 60,
        })
        return ctx


class DiagnosticSubmitView(LoginRequiredMixin, View):
    def post(self, request, attempt_id):
        attempt = get_object_or_404(DiagnosticAttempt, pk=attempt_id, user=request.user)
        data = json.loads(request.body)
        question = get_object_or_404(DiagnosticQuestion, pk=data['question_id'])

        given = data.get('answer', '').strip().upper()
        is_correct = given == question.correct_answer.strip().upper()

        DiagnosticAnswer.objects.update_or_create(
            attempt=attempt, question=question,
            defaults={'given_answer': given, 'is_correct': is_correct,
                      'points_earned': question.points if is_correct else 0}
        )
        return JsonResponse({'is_correct': is_correct, 'correct_answer': question.correct_answer,
                             'explanation': question.explanation})


class DiagnosticCompleteView(LoginRequiredMixin, View):
    def post(self, request, attempt_id):
        attempt = get_object_or_404(DiagnosticAttempt, pk=attempt_id, user=request.user)
        answers = attempt.answers.all()
        score = sum(a.points_earned for a in answers)
        max_score = sum(q.points for q in attempt.test.questions.all())
        percentage = int((score / max_score) * 100) if max_score else 0
        cefr = score_to_cefr(percentage)

        attempt.score = score
        attempt.max_score = max_score
        attempt.percentage = percentage
        attempt.cefr_level = cefr
        attempt.recommendation = RECOMMENDATIONS.get(cefr, '')
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # Update skill progress if applicable
        try:
            from apps.skills.models import SkillProgress
            skill_map = {
                'grammar': 'grammar', 'vocabulary': 'vocabulary',
                'reading': 'reading', 'listening': 'listening', 'writing': 'writing',
            }
            if attempt.test.test_type in skill_map:
                sp, _ = SkillProgress.objects.get_or_create(
                    user=request.user, skill=skill_map[attempt.test.test_type]
                )
                sp.current_score = max(sp.current_score, percentage)
                sp.save(update_fields=['current_score'])
        except Exception:
            pass

        return redirect('diagnostic:results', attempt_id=attempt_id)


class DiagnosticResultsView(LoginRequiredMixin, DetailView):
    model = DiagnosticAttempt
    template_name = 'diagnostic/results.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'

    def get_queryset(self):
        return DiagnosticAttempt.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = self.object
        ctx['answers'] = attempt.answers.select_related('question').all()
        ctx['correct_count'] = attempt.answers.filter(is_correct=True).count()
        ctx['recommendations'] = RECOMMENDATIONS

        # Recommended courses by CEFR
        try:
            from apps.courses.models import Course
            ctx['recommended_courses'] = Course.objects.filter(
                is_published=True, level=CEFR_COURSE_LEVELS.get(attempt.cefr_level, 'A1')
            )[:3]
        except Exception:
            ctx['recommended_courses'] = []
        return ctx
