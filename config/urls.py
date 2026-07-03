from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
import apps.core.views as core_views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', core_views.HomeView.as_view(), name='home'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.courses.urls', namespace='courses')),
    path('vocabulary/', include('apps.vocabulary.urls', namespace='vocabulary')),
    path('grammar/', include('apps.grammar.urls', namespace='grammar')),
    path('quiz/', include('apps.quiz.urls', namespace='quiz')),
    path('gamification/', include('apps.gamification.urls', namespace='gamification')),
    path('certificates/', include('apps.certificates.urls', namespace='certificates')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    # Academic modules
    path('roadmap/', include('apps.roadmap.urls', namespace='roadmap')),
    path('calendar/', include('apps.study_calendar.urls', namespace='study_calendar')),
    path('portfolio/', include('apps.portfolio.urls', namespace='portfolio')),
    path('diagnostic/', include('apps.diagnostic.urls', namespace='diagnostic')),
    path('skills/', include('apps.skills.urls', namespace='skills')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('journal/', include('apps.journal.urls', namespace='journal')),
    path('forum/', include('apps.forum.urls', namespace='forum')),
    path('feedback/', include('apps.feedback.urls', namespace='feedback')),
    path('learning-path/', include('apps.learning_path.urls', namespace='learning_path')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
