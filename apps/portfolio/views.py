from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
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
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        portfolio.bio = request.POST.get('bio', '')
        portfolio.skills_summary = request.POST.get('skills_summary', '')
        portfolio.goals = request.POST.get('goals', '')
        portfolio.is_public = bool(request.POST.get('is_public'))
        portfolio.save()
        messages.success(request, _('Portfolio updated!'))
        return redirect('portfolio:view')


class PortfolioItemAddView(LoginRequiredMixin, View):
    def post(self, request):
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
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
        p.drawString(40, 30, f'Generated by Rustili Platform — {timezone.localdate()}')
        p.save()
        buffer.seek(0)

        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="portfolio_{user.id}.pdf"'
        return resp
