from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils.translation import gettext_lazy as _
import io

from .models import Portfolio, PortfolioItem
from apps.courses.models import Enrollment
from apps.gamification.models import Achievement
from apps.certificates.models import Certificate


class PortfolioView(LoginRequiredMixin, TemplateView):
    template_name = 'portfolio/view.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        portfolio, _ = Portfolio.objects.get_or_create(user=user)
        ctx['portfolio'] = portfolio
        ctx['items'] = portfolio.items.all().order_by('-date')
        ctx['items_by_type'] = {
            t: portfolio.items.filter(item_type=t) for t, _ in PortfolioItem.TYPE_CHOICES
        }
        ctx['enrollments'] = Enrollment.objects.filter(user=user, is_completed=True).select_related('course')
        ctx['certificates'] = Certificate.objects.filter(user=user).select_related('course')
        ctx['achievements'] = Achievement.objects.filter(
            userachievement__user=user
        ).order_by('-userachievement__earned_at')
        try:
            from apps.gamification.models import UserProgress
            ctx['progress'] = UserProgress.objects.get(user=user)
        except Exception:
            ctx['progress'] = None
        return ctx


class PortfolioEditView(LoginRequiredMixin, TemplateView):
    template_name = 'portfolio/edit.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        ctx['portfolio'] = portfolio
        ctx['item_types'] = PortfolioItem.TYPE_CHOICES
        return ctx

    def post(self, request):
        portfolio, _created = Portfolio.objects.get_or_create(user=request.user)
        portfolio.bio = request.POST.get('bio', '')
        portfolio.skills_summary = request.POST.get('skills_summary', '')
        portfolio.goals = request.POST.get('goals', '')
        portfolio.is_public = bool(request.POST.get('is_public'))
        portfolio.save()
        messages.success(request, _('Portfolio updated!'))
        return redirect('portfolio:view')


class PortfolioItemAddView(LoginRequiredMixin, View):
    def post(self, request):
        portfolio, _created = Portfolio.objects.get_or_create(user=request.user)
        item = PortfolioItem(
            portfolio=portfolio,
            item_type=request.POST.get('item_type', 'writing'),
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
        )
        if 'file' in request.FILES:
            item.file = request.FILES['file']
        item.save()
        messages.success(request, _('Item added to portfolio!'))
        return redirect('portfolio:view')


class PortfolioItemDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        PortfolioItem.objects.filter(pk=pk, portfolio__user=request.user).delete()
        return redirect('portfolio:view')


class AdminReviewAccessMixin:
    """Restricts access to staff, teachers and admins."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_staff or getattr(request.user, 'role', '') in ('teacher', 'admin')):
            messages.error(request, _('Access denied.'))
            return redirect('courses:dashboard')
        return super().dispatch(request, *args, **kwargs)


class AdminPortfolioReviewListView(AdminReviewAccessMixin, ListView):
    model = PortfolioItem
    template_name = 'portfolio/admin_review.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = PortfolioItem.objects.select_related(
            'portfolio__user', 'rated_by'
        ).order_by('-created_at')
        status = self.request.GET.get('status')
        if status == 'unrated':
            qs = qs.filter(rating__isnull=True)
        elif status == 'rated':
            qs = qs.filter(rating__isnull=False)
        item_type = self.request.GET.get('type')
        if item_type:
            qs = qs.filter(item_type=item_type)
        if self.request.GET.get('files') == '1':
            qs = qs.exclude(file='').exclude(file__isnull=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        all_items = PortfolioItem.objects.all()
        ctx['total_count'] = all_items.count()
        ctx['unrated_count'] = all_items.filter(rating__isnull=True).count()
        ctx['rated_count'] = all_items.filter(rating__isnull=False).count()
        ctx['avg_rating'] = all_items.filter(rating__isnull=False).aggregate(v=Avg('rating'))['v']
        ctx['item_types'] = PortfolioItem.TYPE_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_type'] = self.request.GET.get('type', '')
        ctx['files_only'] = self.request.GET.get('files') == '1'
        ctx['star_range'] = [5, 4, 3, 2, 1]
        return ctx


class AdminPortfolioRateView(AdminReviewAccessMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(PortfolioItem, pk=pk)
        next_url = request.POST.get('next', '')
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = None

        try:
            rating = int(request.POST.get('rating', ''))
        except (TypeError, ValueError):
            rating = 0
        if not 1 <= rating <= 5:
            messages.error(request, _('Please select a rating from 1 to 5 stars.'))
            return redirect(next_url or 'portfolio:admin-review')

        item.rating = rating
        item.rated_by = request.user
        item.rated_at = timezone.now()
        feedback = request.POST.get('teacher_feedback', '').strip()
        if feedback:
            item.teacher_feedback = feedback
        item.save()
        messages.success(request, _('Rating saved: %(stars)s') % {'stars': item.stars_display})
        return redirect(next_url or 'portfolio:admin-review')


class PortfolioPDFView(LoginRequiredMixin, View):
    def get(self, request):
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors

        user = request.user
        portfolio, _ = Portfolio.objects.get_or_create(user=user)
        enrollments = Enrollment.objects.filter(user=user, is_completed=True).select_related('course')
        certificates = Certificate.objects.filter(user=user)

        buffer = io.BytesIO()
        p = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4

        # Header
        p.setFillColorRGB(0.39, 0.40, 0.95)
        p.rect(0, h - 120, w, 120, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont('Helvetica-Bold', 24)
        p.drawString(40, h - 55, user.get_full_name() or user.email)
        p.setFont('Helvetica', 12)
        p.drawString(40, h - 78, user.email)

        try:
            from apps.gamification.models import UserProgress
            up = UserProgress.objects.get(user=user)
            p.drawString(40, h - 98, f'Level {up.level}  |  {up.xp} XP  |  Streak: {up.streak_days} days')
        except Exception:
            pass

        y = h - 150
        p.setFillColor(colors.black)

        def section(title, ypos):
            p.setFont('Helvetica-Bold', 14)
            p.setFillColorRGB(0.39, 0.40, 0.95)
            p.drawString(40, ypos, title)
            p.setFillColor(colors.black)
            p.line(40, ypos - 4, w - 40, ypos - 4)
            return ypos - 20

        # Bio
        if portfolio.bio:
            y = section('Professional Bio', y)
            p.setFont('Helvetica', 10)
            for line in portfolio.bio[:400].split('\n')[:6]:
                p.drawString(50, y, line[:100])
                y -= 15

        y -= 10
        y = section('Completed Courses', y)
        p.setFont('Helvetica', 10)
        for e in enrollments[:10]:
            p.drawString(50, y, f'• {e.course.title} ({e.course.get_level_display()})')
            y -= 14
            if y < 60:
                p.showPage()
                y = h - 60

        y -= 10
        y = section(f'Certificates ({certificates.count()})', y)
        for cert in certificates[:8]:
            p.drawString(50, y, f'• {cert.course.title} — {cert.issued_at.strftime("%Y-%m-%d")}')
            y -= 14

        # Portfolio items
        items = portfolio.items.all()[:10]
        if items:
            y -= 10
            y = section('Portfolio Works', y)
            for item in items:
                p.setFont('Helvetica-Bold', 10)
                p.drawString(50, y, f'{item.type_icon} {item.title}')
                p.setFont('Helvetica', 9)
                if item.description:
                    p.drawString(60, y - 12, item.description[:80])
                y -= 26

        p.setFont('Helvetica', 8)
        p.setFillColorRGB(0.5, 0.5, 0.5)
        p.drawString(40, 30, f'Generated by LingvoCompetence — {timezone.localdate()}')
        p.save()
        buffer.seek(0)

        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="portfolio_{user.id}.pdf"'
        return resp
