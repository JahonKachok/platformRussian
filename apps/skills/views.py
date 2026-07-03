from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone

from .models import SkillProgress

ALL_SKILLS = ['reading', 'listening', 'speaking', 'writing', 'grammar', 'vocabulary']


def get_or_create_all_skills(user):
    existing = {sp.skill: sp for sp in SkillProgress.objects.filter(user=user)}
    result = []
    for skill in ALL_SKILLS:
        if skill not in existing:
            sp = SkillProgress.objects.create(user=user, skill=skill)
        else:
            sp = existing[skill]
        result.append(sp)
    return result


class SkillsView(LoginRequiredMixin, TemplateView):
    template_name = 'skills/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        skills = get_or_create_all_skills(self.request.user)

        # Determine strengths and weaknesses
        sorted_skills = sorted(skills, key=lambda s: s.current_score, reverse=True)
        strengths = sorted_skills[:2]
        weaknesses = sorted_skills[-2:]

        skill_data = []
        for sp in skills:
            skill_data.append({
                'obj': sp,
                'is_strength': sp in strengths,
                'is_weakness': sp in weaknesses,
                'recommendations': _get_recommendations(sp),
            })

        ctx['skills'] = skill_data
        ctx['overall_score'] = sum(s.current_score for s in skills) // len(skills) if skills else 0
        ctx['total_xp'] = sum(s.weekly_xp for s in skills)
        return ctx


def _get_recommendations(sp):
    tips = {
        'reading': ['Read 1 article daily', 'Practice skimming', 'Expand vocabulary with context'],
        'listening': ['Watch English podcasts', 'Practice note-taking', 'Focus on connected speech'],
        'speaking': ['Record yourself daily', 'Practice pronunciation', 'Use shadowing technique'],
        'writing': ['Write a short paragraph daily', 'Focus on sentence variety', 'Review grammar rules'],
        'grammar': ['Review one rule per day', 'Practice with exercises', 'Read grammar explanations'],
        'vocabulary': ['Learn 10 words daily', 'Use flashcards', 'Read in context'],
    }
    return tips.get(sp.skill, [])
