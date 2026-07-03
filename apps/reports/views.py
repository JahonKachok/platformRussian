from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse
from django.utils import timezone
import io
from datetime import timedelta


class ReportsIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            from apps.courses.models import Enrollment, LessonProgress
            from apps.quiz.models import QuizAttempt
            from apps.certificates.models import Certificate
            from apps.gamification.models import UserProgress

            ctx['enrollment_count'] = Enrollment.objects.filter(user=user).count()
            ctx['completed_count'] = Enrollment.objects.filter(user=user, is_completed=True).count()
            ctx['lessons_done'] = LessonProgress.objects.filter(user=user, is_completed=True).count()
            ctx['quiz_attempts'] = QuizAttempt.objects.filter(user=user, completed=True).count()
            ctx['certificates'] = Certificate.objects.filter(user=user).count()
            ctx['progress'] = UserProgress.objects.get(user=user)
        except Exception:
            pass
        return ctx


def _build_pdf_header(p, user, title, w, h):
    from reportlab.lib import colors
    p.setFillColorRGB(0.39, 0.40, 0.95)
    p.rect(0, h - 100, w, 100, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 20)
    p.drawString(40, h - 45, title)
    p.setFont('Helvetica', 11)
    p.drawString(40, h - 65, f'Student: {user.get_full_name() or user.email}')
    p.drawString(40, h - 82, f'Generated: {timezone.localdate()}')
    p.setFillColor(colors.black)
    return h - 120


class ProgressReportPDFView(LoginRequiredMixin, View):
    def get(self, request):
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors

        user = request.user
        buffer = io.BytesIO()
        p = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4

        y = _build_pdf_header(p, user, 'Progress Report', w, h)

        try:
            from apps.gamification.models import UserProgress
            from apps.courses.models import Enrollment, LessonProgress
            from apps.quiz.models import QuizAttempt

            up = UserProgress.objects.get(user=user)

            p.setFont('Helvetica-Bold', 13)
            p.setFillColorRGB(0.39, 0.40, 0.95)
            p.drawString(40, y, 'Overall Progress')
            p.line(40, y - 4, w - 40, y - 4)
            p.setFillColor(colors.black)
            y -= 25

            stats = [
                ('Level', str(up.level)),
                ('Total XP', f'{up.xp:,}'),
                ('Streak', f'{up.streak_days} days'),
                ('Daily XP', str(up.daily_xp)),
                ('Enrolled Courses', str(Enrollment.objects.filter(user=user).count())),
                ('Completed Courses', str(Enrollment.objects.filter(user=user, is_completed=True).count())),
                ('Lessons Completed', str(LessonProgress.objects.filter(user=user, is_completed=True).count())),
                ('Quizzes Passed', str(QuizAttempt.objects.filter(user=user, completed=True, passed=True).count())),
            ]
            p.setFont('Helvetica', 11)
            for label, val in stats:
                p.drawString(50, y, f'{label}:')
                p.drawString(220, y, val)
                y -= 18

            # Course progress
            y -= 15
            p.setFont('Helvetica-Bold', 13)
            p.setFillColorRGB(0.39, 0.40, 0.95)
            p.drawString(40, y, 'Course Progress')
            p.line(40, y - 4, w - 40, y - 4)
            p.setFillColor(colors.black)
            y -= 25
            p.setFont('Helvetica', 10)
            for e in Enrollment.objects.filter(user=user).select_related('course').order_by('-progress_percent'):
                status = '✓ Completed' if e.is_completed else f'{e.progress_percent}%'
                p.drawString(50, y, f'• {e.course.title}')
                p.drawString(350, y, status)
                y -= 15
                if y < 60:
                    p.showPage(); y = h - 60

        except Exception as e:
            p.setFont('Helvetica', 11)
            p.drawString(40, y, f'Error generating report: {e}')

        p.setFont('Helvetica', 8)
        p.setFillColorRGB(0.5, 0.5, 0.5)
        p.drawString(40, 30, 'LingvoCompetence — Russian Language Learning Platform')
        p.save()
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="progress_report_{user.id}.pdf"'
        return resp


class QuizReportPDFView(LoginRequiredMixin, View):
    def get(self, request):
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors

        user = request.user
        buffer = io.BytesIO()
        p = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4

        y = _build_pdf_header(p, user, 'Quiz Performance Report', w, h)

        try:
            from apps.quiz.models import QuizAttempt
            attempts = QuizAttempt.objects.filter(user=user, completed=True).select_related('quiz').order_by('-completed_at')

            p.setFont('Helvetica-Bold', 11)
            headers = [('Quiz', 40), ('Score', 280), ('Status', 360), ('Date', 430)]
            for label, x in headers:
                p.drawString(x, y, label)
            y -= 5
            p.line(40, y, w - 40, y)
            y -= 15

            p.setFont('Helvetica', 10)
            for attempt in attempts[:30]:
                p.drawString(40, y, attempt.quiz.title[:35])
                p.drawString(280, y, f'{attempt.percentage}%')
                p.drawString(360, y, 'Passed' if attempt.passed else 'Failed')
                p.drawString(430, y, attempt.completed_at.strftime('%Y-%m-%d') if attempt.completed_at else '-')
                y -= 14
                if y < 60:
                    p.showPage(); y = h - 60

        except Exception:
            pass

        p.save()
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="quiz_report_{user.id}.pdf"'
        return resp


class AdminAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/admin_analytics.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            from django.shortcuts import redirect
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from apps.accounts.models import User
            from apps.courses.models import Course, Enrollment, LessonProgress
            from apps.quiz.models import QuizAttempt
            from apps.certificates.models import Certificate
            from apps.gamification.models import UserProgress
            from django.db.models import Avg, Count, Sum
            from datetime import timedelta

            today = timezone.localdate()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)

            ctx['total_students'] = User.objects.filter(role='student').count()
            ctx['active_today'] = User.objects.filter(last_active__date=today).count()
            ctx['active_week'] = User.objects.filter(last_active__date__gte=week_ago).count()
            ctx['total_courses'] = Course.objects.filter(is_published=True).count()
            ctx['total_enrollments'] = Enrollment.objects.count()
            ctx['completed_courses'] = Enrollment.objects.filter(is_completed=True).count()
            ctx['total_certificates'] = Certificate.objects.count()
            ctx['avg_score'] = QuizAttempt.objects.filter(completed=True).aggregate(a=Avg('percentage'))['a'] or 0
            ctx['total_teachers'] = User.objects.filter(role='teacher').count()
            ctx['popular_courses'] = Course.objects.filter(is_published=True).annotate(
                enroll_count=Count('enrollments')
            ).order_by('-enroll_count')[:5]
            ctx['recent_users'] = User.objects.order_by('-date_joined')[:10]
            ctx['top_students'] = UserProgress.objects.select_related('user').order_by('-xp')[:10]
            ctx['lessons_completed_total'] = LessonProgress.objects.filter(is_completed=True).count()
        except Exception:
            pass
        return ctx
