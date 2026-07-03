from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import JournalEntry


class JournalListView(LoginRequiredMixin, ListView):
    model = JournalEntry
    template_name = 'journal/index.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user).order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['moods'] = JournalEntry.MOOD_CHOICES
        ctx['total_entries'] = JournalEntry.objects.filter(user=self.request.user).count()
        ctx['avg_rating'] = 0
        entries = JournalEntry.objects.filter(user=self.request.user)
        if entries.exists():
            from django.db.models import Avg
            ctx['avg_rating'] = round(entries.aggregate(a=Avg('self_rating'))['a'] or 0, 1)
        return ctx


class JournalEntryView(LoginRequiredMixin, DetailView):
    model = JournalEntry
    template_name = 'journal/entry.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)


class JournalCreateView(LoginRequiredMixin, View):
    def post(self, request):
        entry = JournalEntry.objects.create(
            user=request.user,
            lesson_id=request.POST.get('lesson_id') or None,
            what_learned=request.POST.get('what_learned', ''),
            what_was_difficult=request.POST.get('what_was_difficult', ''),
            topics_to_revisit=request.POST.get('topics_to_revisit', ''),
            self_rating=int(request.POST.get('self_rating', 3)),
            mood=request.POST.get('mood', 'neutral'),
        )
        messages.success(request, _('Journal entry saved!'))
        return redirect('journal:entry', pk=entry.id)


class JournalDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        JournalEntry.objects.filter(pk=pk, user=request.user).delete()
        return redirect('journal:index')
