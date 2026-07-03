from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
import json
import calendar as cal

from .models import CalendarEvent


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'study_calendar/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        # Build calendar grid using monthcalendar (weeks × 7 days, 0 = empty)
        weeks = cal.monthcalendar(year, month)

        events_qs = CalendarEvent.objects.filter(
            user=self.request.user, date__year=year, date__month=month
        ).order_by('time')

        events_by_day = {}
        for ev in events_qs:
            events_by_day.setdefault(ev.date.day, []).append(ev)

        # Prev/Next
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        ctx.update({
            'year': year, 'month': month,
            'month_name': cal.month_name[month],
            'weeks': weeks,
            'events_by_day': events_by_day,
            'today': today,
            'prev_year': prev_year, 'prev_month': prev_month,
            'next_year': next_year, 'next_month': next_month,
            'event_types': CalendarEvent.TYPE_CHOICES,
            'upcoming': CalendarEvent.objects.filter(
                user=self.request.user, date__gte=today
            ).order_by('date', 'time')[:5],
        })
        return ctx


class EventCreateView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        event = CalendarEvent.objects.create(
            user=request.user,
            title=data.get('title', ''),
            event_type=data.get('event_type', 'reminder'),
            date=data.get('date'),
            time=data.get('time') or None,
            description=data.get('description', ''),
        )
        return JsonResponse({
            'id': event.id, 'title': event.title,
            'color': event.get_color(), 'event_type': event.event_type,
        })


class EventToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            event = CalendarEvent.objects.get(pk=pk, user=request.user)
            event.is_completed = not event.is_completed
            event.save(update_fields=['is_completed'])
            return JsonResponse({'is_completed': event.is_completed})
        except CalendarEvent.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)


class EventDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        CalendarEvent.objects.filter(pk=pk, user=request.user).delete()
        return JsonResponse({'status': 'ok'})
