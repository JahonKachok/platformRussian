from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        stats = cache.get('home_stats')
        if not stats:
            try:
                from apps.accounts.models import User
                from apps.courses.models import Course
                from apps.gamification.models import UserProgress
                stats = {
                    'total_students': User.objects.filter(is_staff=False).count(),
                    'total_courses': Course.objects.filter(is_published=True).count(),
                    'total_lessons': 0,
                    'completion_rate': 94,
                }
                from apps.courses.models import Lesson
                stats['total_lessons'] = Lesson.objects.filter(is_published=True).count()
            except Exception:
                stats = {
                    'total_students': 0,
                    'total_courses': 0,
                    'total_lessons': 0,
                    'completion_rate': 94,
                }
            cache.set('home_stats', stats, 300)

        ctx['stats'] = stats

        try:
            from apps.courses.models import Course
            ctx['featured_courses'] = Course.objects.filter(
                is_published=True, is_featured=True
            ).order_by('-created_at')[:6]
        except Exception:
            ctx['featured_courses'] = []

        try:
            from apps.accounts.models import User
            ctx['teachers'] = User.objects.filter(role='teacher', is_active=True)[:4]
        except Exception:
            ctx['teachers'] = []

        return ctx


class Error404View(TemplateView):
    template_name = 'pages/404.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


class Error500View(TemplateView):
    template_name = 'pages/500.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 500
        return response
