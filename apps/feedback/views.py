from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, ListView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import HomeworkSubmission, TeacherFeedback
from apps.courses.models import Lesson


class FeedbackStudentView(LoginRequiredMixin, TemplateView):
    template_name = 'feedback/student.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['submissions'] = HomeworkSubmission.objects.filter(
            user=user
        ).select_related('lesson__course', 'feedback').order_by('-created_at')
        ctx['pending_count'] = HomeworkSubmission.objects.filter(user=user, status='pending').count()
        ctx['reviewed_count'] = HomeworkSubmission.objects.filter(user=user, status='reviewed').count()
        return ctx


class FeedbackSubmitView(LoginRequiredMixin, View):
    def post(self, request, lesson_slug):
        lesson = get_object_or_404(Lesson, slug=lesson_slug, is_published=True)
        sub = HomeworkSubmission(user=request.user, lesson=lesson)
        sub.text = request.POST.get('text', '')
        if 'file' in request.FILES:
            sub.file = request.FILES['file']
        if 'audio' in request.FILES:
            sub.audio = request.FILES['audio']
        sub.save()
        messages.success(request, _('Homework submitted successfully!'))
        return redirect('feedback:student')


class FeedbackDetailView(LoginRequiredMixin, DetailView):
    model = HomeworkSubmission
    template_name = 'feedback/detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        return HomeworkSubmission.objects.filter(user=self.request.user)


class TeacherReviewListView(LoginRequiredMixin, ListView):
    model = HomeworkSubmission
    template_name = 'feedback/teacher_list.html'
    context_object_name = 'submissions'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or getattr(request.user, 'role', '') in ('teacher', 'admin')):
            messages.error(request, _('Access denied.'))
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return HomeworkSubmission.objects.select_related(
            'user', 'lesson__course', 'feedback'
        ).order_by('-created_at')


class TeacherReviewView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or getattr(request.user, 'role', '') in ('teacher', 'admin')):
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        from django.shortcuts import render
        submission = get_object_or_404(HomeworkSubmission, pk=pk)
        try:
            feedback = submission.feedback
        except TeacherFeedback.DoesNotExist:
            feedback = None
        return render(request, 'feedback/review.html', {
            'submission': submission, 'feedback': feedback
        })

    def post(self, request, pk):
        submission = get_object_or_404(HomeworkSubmission, pk=pk)
        fb, _ = TeacherFeedback.objects.get_or_create(submission=submission, defaults={'teacher': request.user})
        fb.teacher = request.user
        fb.text_feedback = request.POST.get('text_feedback', '')
        fb.score = request.POST.get('score') or None
        fb.grammar_score = int(request.POST.get('grammar_score', 0))
        fb.vocabulary_score = int(request.POST.get('vocabulary_score', 0))
        fb.fluency_score = int(request.POST.get('fluency_score', 0))
        fb.content_score = int(request.POST.get('content_score', 0))
        if 'audio_feedback' in request.FILES:
            fb.audio_feedback = request.FILES['audio_feedback']
        fb.save()
        submission.status = 'reviewed'
        submission.save(update_fields=['status'])
        messages.success(request, _('Feedback submitted!'))
        return redirect('feedback:teacher-list')
