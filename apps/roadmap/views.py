from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView
from django.shortcuts import get_object_or_404

from apps.courses.models import Course, Enrollment, LessonProgress


class RoadmapIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'roadmap/index_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        enrollments = Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course').order_by('-enrolled_at')
        ctx['enrollments'] = enrollments
        return ctx


class RoadmapView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'roadmap/index.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(is_published=True).select_related('category', 'teacher')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object

        lessons = list(course.lessons.filter(is_published=True).order_by('order'))
        enrollment = course.get_enrollment(user)

        completed_ids = set()
        if enrollment:
            completed_ids = set(
                LessonProgress.objects.filter(
                    user=user, lesson__course=course, is_completed=True
                ).values_list('lesson_id', flat=True)
            )

        # Build roadmap steps
        steps = []
        for i, lesson in enumerate(lessons):
            if lesson.id in completed_ids:
                state = 'completed'
            elif i == 0 or lessons[i - 1].id in completed_ids:
                state = 'current' if lesson.id not in completed_ids else 'completed'
            else:
                state = 'locked'
            steps.append({'lesson': lesson, 'state': state, 'number': i + 1})

        # Fix: mark first non-completed as current
        found_current = False
        for step in steps:
            if step['state'] == 'locked' and not found_current:
                # Check if all before are completed
                idx = step['number'] - 1
                if idx == 0 or steps[idx - 1]['state'] == 'completed':
                    step['state'] = 'current'
                    found_current = True

        completed_count = sum(1 for s in steps if s['state'] == 'completed')
        total = len(steps)

        # Estimated completion time
        completed_minutes = sum(s['lesson'].duration_minutes for s in steps if s['state'] == 'completed')
        remaining_minutes = sum(s['lesson'].duration_minutes for s in steps if s['state'] != 'completed')

        ctx['steps'] = steps
        ctx['enrollment'] = enrollment
        ctx['completed_count'] = completed_count
        ctx['total_count'] = total
        ctx['progress_percent'] = int((completed_count / total) * 100) if total else 0
        ctx['remaining_minutes'] = remaining_minutes
        ctx['completed_minutes'] = completed_minutes
        return ctx
