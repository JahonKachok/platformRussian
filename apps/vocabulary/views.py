from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from .models import Word, UserWord, WordCategory


class FlashcardsView(LoginRequiredMixin, TemplateView):
    template_name = 'vocabulary/flashcards.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get('category')
        difficulty = self.request.GET.get('difficulty')

        words = Word.objects.all().select_related('category')
        if category_slug:
            words = words.filter(category__slug=category_slug)
        if difficulty:
            words = words.filter(difficulty=difficulty)

        ctx['words'] = words[:20]
        ctx['categories'] = WordCategory.objects.all()
        ctx['difficulties'] = Word.DIFFICULTY_CHOICES

        mastered = UserWord.objects.filter(user=self.request.user, status='mastered').count()
        learning = UserWord.objects.filter(user=self.request.user, status='learning').count()
        total = Word.objects.count()
        ctx['mastered_count'] = mastered
        ctx['learning_count'] = learning
        ctx['total_count'] = total
        return ctx


class VocabularyListView(LoginRequiredMixin, ListView):
    model = Word
    template_name = 'vocabulary/list.html'
    context_object_name = 'words'
    paginate_by = 24

    def get_queryset(self):
        qs = Word.objects.select_related('category').order_by('order', 'word')
        search = self.request.GET.get('q')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        if search:
            qs = qs.filter(word__icontains=search)
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = WordCategory.objects.all()
        user_words = {uw.word_id: uw for uw in UserWord.objects.filter(user=self.request.user)}
        ctx['user_words'] = user_words
        return ctx


class WordStatusView(LoginRequiredMixin, View):
    def post(self, request, word_id):
        import json
        data = json.loads(request.body)
        action = data.get('action')
        word = Word.objects.get(pk=word_id)
        uw, _ = UserWord.objects.get_or_create(user=request.user, word=word)

        if action == 'favorite':
            uw.is_favorite = not uw.is_favorite
            uw.save(update_fields=['is_favorite'])
            return JsonResponse({'status': 'ok', 'is_favorite': uw.is_favorite})
        elif action == 'correct':
            uw.correct_count += 1
            uw.last_reviewed = timezone.now()
            if uw.correct_count >= 5:
                uw.status = 'mastered'
            elif uw.correct_count >= 2:
                uw.status = 'learning'
            uw.save()
            return JsonResponse({'status': 'ok', 'word_status': uw.status})
        elif action == 'incorrect':
            uw.incorrect_count += 1
            uw.last_reviewed = timezone.now()
            uw.save(update_fields=['incorrect_count', 'last_reviewed'])
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'}, status=400)
