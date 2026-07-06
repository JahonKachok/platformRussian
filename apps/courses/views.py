from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from .models import Course, Lesson, Enrollment, LessonProgress, Category


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        enrollments = Enrollment.objects.filter(user=user).select_related('course').order_by('-created_at')
        ctx['enrollments'] = enrollments[:6]
        ctx['total_enrolled'] = enrollments.count()

        recent_progress = LessonProgress.objects.filter(
            user=user
        ).select_related('lesson__course').order_by('-updated_at')[:5]
        ctx['recent_activity'] = recent_progress

        try:
            from apps.gamification.models import UserProgress, Achievement, UserAchievement, LeaderboardEntry
            progress = UserProgress.objects.get(user=user)
            ctx['progress'] = progress

            ctx['achievements'] = Achievement.objects.filter(
                userachievement__user=user
            ).order_by('-userachievement__earned_at')[:4]

            leaderboard = LeaderboardEntry.objects.filter(period='weekly').order_by('rank')[:10]
            ctx['leaderboard'] = leaderboard

            try:
                user_entry = LeaderboardEntry.objects.get(user=user, period='weekly')
                ctx['user_rank'] = user_entry.rank
            except LeaderboardEntry.DoesNotExist:
                ctx['user_rank'] = '-'

        except Exception:
            ctx['progress'] = None
            ctx['achievements'] = []
            ctx['leaderboard'] = []
            ctx['user_rank'] = '-'

        ctx['today'] = timezone.localdate()
        return ctx


class CourseListView(ListView):
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(is_published=True).select_related('category', 'teacher')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        search = self.request.GET.get('q')
        if category:
            qs = qs.filter(category__slug=category)
        if level:
            qs = qs.filter(level=level)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['levels'] = Course.LEVEL_CHOICES
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_level'] = self.request.GET.get('level', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(is_published=True).select_related('category', 'teacher')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object
        ctx['lessons'] = course.lessons.filter(is_published=True).order_by('order')
        ctx['lesson_count'] = ctx['lessons'].count()

        if self.request.user.is_authenticated:
            enrollment = course.get_enrollment(self.request.user)
            ctx['enrollment'] = enrollment
            if enrollment:
                completed_ids = LessonProgress.objects.filter(
                    user=self.request.user, lesson__course=course, is_completed=True
                ).values_list('lesson_id', flat=True)
                ctx['completed_lesson_ids'] = set(completed_ids)
            else:
                ctx['completed_lesson_ids'] = set()

        return ctx


class EnrollView(LoginRequiredMixin, View):
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        if created:
            messages.success(request, _('Successfully enrolled in course!'))
            try:
                from apps.notifications.utils import notify
                from apps.notifications.models import Notification
                notify(
                    user=request.user,
                    title=f'"{course.title}" kursiga yozildingiz',
                    message=f'Tabriklaymiz! Siz "{course.title}" kursini boshlashga tayyorsiz.',
                    notification_type=Notification.TYPE_LESSON,
                    icon='📚',
                )
            except Exception:
                pass
        return redirect('courses:course-detail', slug=slug)


class LessonView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson.html'
    context_object_name = 'lesson'
    slug_url_kwarg = 'lesson_slug'

    def get_queryset(self):
        return Lesson.objects.filter(is_published=True).select_related('course')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        lesson = self.get_object()
        if not lesson.is_free_preview:
            enrollment = lesson.course.get_enrollment(request.user)
            if not enrollment:
                messages.warning(request, _('Please enroll in this course first.'))
                return redirect('courses:course-detail', slug=lesson.course.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lesson = self.object
        ctx['course'] = lesson.course
        ctx['lessons'] = lesson.course.lessons.filter(is_published=True).order_by('order')

        try:
            progress = LessonProgress.objects.get(user=self.request.user, lesson=lesson)
            ctx['lesson_progress'] = progress
        except LessonProgress.DoesNotExist:
            ctx['lesson_progress'] = None

        # Next/Prev lesson
        all_lessons = list(lesson.course.lessons.filter(is_published=True).order_by('order'))
        idx = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
        ctx['prev_lesson'] = all_lessons[idx - 1] if idx and idx > 0 else None
        ctx['next_lesson'] = all_lessons[idx + 1] if idx is not None and idx < len(all_lessons) - 1 else None

        return ctx


class CompleteLessonView(LoginRequiredMixin, View):
    def post(self, request, lesson_slug):
        lesson = get_object_or_404(Lesson, slug=lesson_slug, is_published=True)
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save(update_fields=['is_completed', 'completed_at'])

            # Update enrollment progress
            enrollment = lesson.course.get_enrollment(request.user)
            if enrollment:
                total = lesson.course.lessons.filter(is_published=True).count()
                completed = LessonProgress.objects.filter(
                    user=request.user, lesson__course=lesson.course, is_completed=True
                ).count()
                enrollment.progress_percent = int((completed / total) * 100) if total else 0
                enrollment.completed_lessons = completed
                if enrollment.progress_percent >= 100:
                    enrollment.is_completed = True
                    enrollment.completed_at = timezone.now()
                enrollment.save()

            # Add XP
            try:
                from apps.gamification.models import UserProgress
                up = UserProgress.objects.get(user=request.user)
                up.add_xp(lesson.xp_reward, 'lesson_complete')
                up.total_lessons_completed += 1
                up.save(update_fields=['total_lessons_completed'])
            except Exception:
                pass

            # Notify lesson complete
            try:
                from apps.notifications.utils import notify
                from apps.notifications.models import Notification
                notify(
                    user=request.user,
                    title=f'Dars yakunlandi: {lesson.title}',
                    message=f'Siz "{lesson.title}" darsini muvaffaqiyatli tugatdingiz. +{lesson.xp_reward} XP.',
                    notification_type=Notification.TYPE_LESSON,
                    icon='✅',
                )
            except Exception:
                pass

            # Notify course complete
            if enrollment and enrollment.is_completed:
                try:
                    from apps.notifications.utils import notify
                    from apps.notifications.models import Notification
                    notify(
                        user=request.user,
                        title=f'Kurs yakunlandi: {lesson.course.title}',
                        message=f'Tabriklaymiz! Siz "{lesson.course.title}" kursini to\'liq tugatdingiz. Sertifikat olish uchun sertifikatlar bo\'limiga o\'ting.',
                        notification_type=Notification.TYPE_CERTIFICATE,
                        icon='🎓',
                    )
                except Exception:
                    pass

        return JsonResponse({'status': 'ok', 'xp': lesson.xp_reward})
