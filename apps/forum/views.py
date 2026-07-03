from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import ForumTopic, ForumReply, ForumLike
from apps.courses.models import Course


class ForumIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'forum/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Show forums for courses user is enrolled in
        user = self.request.user
        enrolled_courses = Course.objects.filter(
            enrollments__user=user, is_published=True
        ).distinct()
        ctx['courses'] = enrolled_courses
        ctx['recent_topics'] = ForumTopic.objects.filter(
            course__in=enrolled_courses
        ).select_related('author', 'course').order_by('-created_at')[:10]
        return ctx


class ForumCourseView(LoginRequiredMixin, TemplateView):
    template_name = 'forum/course.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, slug=kwargs['slug'], is_published=True)
        search = self.request.GET.get('q', '')
        topics = ForumTopic.objects.filter(course=course).select_related('author')
        if search:
            topics = topics.filter(Q(title__icontains=search) | Q(content__icontains=search))

        ctx['course'] = course
        ctx['topics'] = topics.order_by('-is_pinned', '-is_announcement', '-created_at')
        ctx['search'] = search
        return ctx


class ForumTopicView(LoginRequiredMixin, DetailView):
    model = ForumTopic
    template_name = 'forum/topic.html'
    context_object_name = 'topic'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        replies = self.object.replies.select_related('author').all()
        liked_topic_ids = set(
            ForumLike.objects.filter(user=user, topic=self.object).values_list('topic_id', flat=True)
        )
        liked_reply_ids = set(
            ForumLike.objects.filter(user=user, reply__in=replies).values_list('reply_id', flat=True)
        )
        ctx['replies'] = replies
        ctx['liked_topic'] = self.object.id in liked_topic_ids
        ctx['liked_reply_ids'] = liked_reply_ids
        return ctx


class ForumTopicCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if title and content:
            topic = ForumTopic.objects.create(
                course=course, author=request.user, title=title, content=content,
            )
            if 'attachment' in request.FILES:
                topic.attachment = request.FILES['attachment']
                topic.save(update_fields=['attachment'])
            messages.success(request, _('Topic created!'))
            return redirect('forum:topic', pk=topic.id)
        messages.error(request, _('Title and content are required.'))
        return redirect('forum:course', slug=slug)


class ForumReplyCreateView(LoginRequiredMixin, View):
    def post(self, request, topic_id):
        topic = get_object_or_404(ForumTopic, pk=topic_id)
        if topic.is_locked and not request.user.is_staff:
            messages.error(request, _('This topic is locked.'))
            return redirect('forum:topic', pk=topic_id)
        content = request.POST.get('content', '').strip()
        if content:
            reply = ForumReply.objects.create(topic=topic, author=request.user, content=content)
            if 'attachment' in request.FILES:
                reply.attachment = request.FILES['attachment']
                reply.save(update_fields=['attachment'])
        return redirect('forum:topic', pk=topic_id)


class ForumLikeView(LoginRequiredMixin, View):
    def post(self, request):
        data_type = request.POST.get('type')
        pk = int(request.POST.get('pk', 0))
        if data_type == 'topic':
            obj, created = ForumLike.objects.get_or_create(user=request.user, topic_id=pk, reply=None)
            if not created:
                obj.delete()
                liked = False
            else:
                liked = True
            count = ForumLike.objects.filter(topic_id=pk).count()
        else:
            obj, created = ForumLike.objects.get_or_create(user=request.user, reply_id=pk, topic=None)
            if not created:
                obj.delete()
                liked = False
            else:
                liked = True
            count = ForumLike.objects.filter(reply_id=pk).count()
        return JsonResponse({'liked': liked, 'count': count})
