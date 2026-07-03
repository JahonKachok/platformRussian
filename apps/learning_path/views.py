from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone

from .models import LearningPathItem


def generate_path(user):
    """Rule-based learning path generator."""
    items = []
    try:
        from apps.gamification.models import UserProgress
        from apps.courses.models import Enrollment, Lesson
        from apps.skills.models import SkillProgress

        progress = UserProgress.objects.get(user=user)
        level = progress.level

        # Suggest lessons from enrolled but incomplete courses
        from apps.courses.models import LessonProgress
        enrolled = Enrollment.objects.filter(user=user, is_completed=False).select_related('course')
        for enrollment in enrolled[:2]:
            completed_ids = set(
                LessonProgress.objects.filter(
                    user=user, lesson__course=enrollment.course, is_completed=True
                ).values_list('lesson_id', flat=True)
            )
            next_lesson = enrollment.course.lessons.filter(
                is_published=True
            ).exclude(id__in=completed_ids).order_by('order').first()
            if next_lesson:
                items.append({
                    'content_type': 'lesson',
                    'content_id': next_lesson.id,
                    'title': next_lesson.title,
                    'description': f'Continue: {enrollment.course.title}',
                    'reason': 'Next lesson in your enrolled course',
                    'priority': 1,
                    'estimated_minutes': next_lesson.duration_minutes,
                })

        # Suggest vocabulary if score < 50
        skill_scores = {sp.skill: sp.current_score for sp in SkillProgress.objects.filter(user=user)}
        if skill_scores.get('vocabulary', 0) < 50:
            items.append({
                'content_type': 'vocabulary',
                'content_id': None,
                'title': 'Vocabulary Flashcards',
                'description': 'Boost your vocabulary score',
                'reason': f'Your vocabulary score is {skill_scores.get("vocabulary", 0)}% — below target',
                'priority': 2,
                'estimated_minutes': 15,
            })

        # Suggest grammar if score < 50
        if skill_scores.get('grammar', 0) < 50:
            from apps.grammar.models import GrammarTopic
            topic = GrammarTopic.objects.filter(is_published=True).order_by('order').first()
            if topic:
                items.append({
                    'content_type': 'grammar',
                    'content_id': topic.id,
                    'title': topic.title,
                    'description': 'Grammar review recommended',
                    'reason': f'Grammar score: {skill_scores.get("grammar", 0)}% — needs improvement',
                    'priority': 2,
                    'estimated_minutes': 20,
                })

        # Suggest diagnostic if no attempts yet
        from apps.diagnostic.models import DiagnosticAttempt, DiagnosticTest
        has_placement = DiagnosticAttempt.objects.filter(
            user=user, completed=True, test__test_type='placement'
        ).exists()
        if not has_placement:
            test = DiagnosticTest.objects.filter(test_type='placement', is_active=True).first()
            if test:
                items.append({
                    'content_type': 'diagnostic',
                    'content_id': test.id,
                    'title': test.title,
                    'description': 'Determine your English level',
                    'reason': 'Taking a placement test helps personalize your learning',
                    'priority': 0,
                    'estimated_minutes': test.time_limit_minutes,
                })

    except Exception:
        pass

    return items


class LearningPathView(LoginRequiredMixin, TemplateView):
    template_name = 'learning_path/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        saved = list(LearningPathItem.objects.filter(user=user).order_by('is_completed', 'priority'))

        # Auto-generate and save if empty or outdated
        if not saved or not any(not item.is_completed for item in saved):
            LearningPathItem.objects.filter(user=user, is_completed=False).delete()
            generated = generate_path(user)
            new_items = []
            for item_data in generated:
                exists = LearningPathItem.objects.filter(
                    user=user, content_type=item_data['content_type'],
                    content_id=item_data.get('content_id'), is_completed=False
                ).exists()
                if not exists:
                    new_items.append(LearningPathItem(user=user, **item_data))
            if new_items:
                LearningPathItem.objects.bulk_create(new_items)
            saved = list(LearningPathItem.objects.filter(user=user).order_by('is_completed', 'priority'))

        ctx['items'] = saved
        ctx['pending_count'] = sum(1 for i in saved if not i.is_completed)
        ctx['completed_count'] = sum(1 for i in saved if i.is_completed)
        ctx['total_minutes'] = sum(i.estimated_minutes for i in saved if not i.is_completed)
        return ctx


class LearningPathCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = LearningPathItem.objects.filter(pk=pk, user=request.user).first()
        if item:
            item.is_completed = True
            item.completed_at = timezone.now()
            item.save(update_fields=['is_completed', 'completed_at'])
        return JsonResponse({'status': 'ok'})


class LearningPathRefreshView(LoginRequiredMixin, View):
    def post(self, request):
        LearningPathItem.objects.filter(user=request.user, is_completed=False).delete()
        return redirect('learning_path:index')
