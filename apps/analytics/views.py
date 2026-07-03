from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum, Avg, Count
import json
from datetime import timedelta

from .models import StudySession


def get_or_create_today(user):
    today = timezone.localdate()
    session, _ = StudySession.objects.get_or_create(user=user, date=today)
    return session


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        # Date ranges
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        sessions = StudySession.objects.filter(user=user)

        daily = sessions.filter(date=today).first()
        weekly = sessions.filter(date__gte=week_start).aggregate(
            mins=Sum('minutes_studied'), xp=Sum('xp_earned'),
            lessons=Sum('lessons_completed'), quizzes=Sum('quizzes_completed')
        )
        monthly = sessions.filter(date__gte=month_start).aggregate(
            mins=Sum('minutes_studied'), xp=Sum('xp_earned')
        )

        # Last 30 days for heatmap / chart
        last_30 = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            s = sessions.filter(date=d).first()
            last_30.append({
                'date': d.strftime('%Y-%m-%d'),
                'day': d.strftime('%d'),
                'mins': s.minutes_studied if s else 0,
                'xp': s.xp_earned if s else 0,
                'weekday': d.weekday(),
            })

        # Heatmap: last 12 weeks (Sun to Sat)
        heatmap = []
        for i in range(83, -1, -1):
            d = today - timedelta(days=i)
            s = sessions.filter(date=d).first()
            mins = s.minutes_studied if s else 0
            intensity = 0 if mins == 0 else (1 if mins < 15 else (2 if mins < 30 else (3 if mins < 60 else 4)))
            heatmap.append({'date': d.strftime('%b %d'), 'intensity': intensity, 'mins': mins})

        # Most active day of week
        dow_data = sessions.extra(select={'dow': "strftime('%w', date)"}).values('dow').annotate(
            total=Sum('minutes_studied')
        ).order_by('-total')
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        most_active = days[int(dow_data[0]['dow'])] if dow_data else 'N/A'

        # Weekly chart data (last 7 days)
        weekly_chart = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            s = sessions.filter(date=d).first()
            weekly_chart.append({
                'label': d.strftime('%a'),
                'mins': s.minutes_studied if s else 0,
                'xp': s.xp_earned if s else 0,
            })

        ctx.update({
            'daily': daily,
            'weekly': weekly,
            'monthly': monthly,
            'last_30': last_30,
            'heatmap': heatmap,
            'most_active': most_active,
            'weekly_chart_json': json.dumps(weekly_chart),
            'heatmap_json': json.dumps(heatmap),
            'total_sessions': sessions.count(),
            'avg_daily': int(sessions.aggregate(a=Avg('minutes_studied'))['a'] or 0),
        })
        return ctx
