from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class ForumTopic(TimeStampedModel):
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='forum_topics'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_topics'
    )
    title = models.CharField(_('Title'), max_length=300)
    content = models.TextField(_('Content'))
    is_pinned = models.BooleanField(_('Pinned'), default=False)
    is_announcement = models.BooleanField(_('Announcement'), default=False)
    is_locked = models.BooleanField(_('Locked'), default=False)
    views = models.PositiveIntegerField(_('Views'), default=0)
    attachment = models.FileField(_('Attachment'), upload_to='forum/attachments/', null=True, blank=True)

    class Meta:
        verbose_name = _('Forum Topic')
        verbose_name_plural = _('Forum Topics')
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def like_count(self):
        return self.likes.filter(topic=self).count()


class ForumReply(TimeStampedModel):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_replies'
    )
    content = models.TextField(_('Content'))
    is_solution = models.BooleanField(_('Solution'), default=False)
    attachment = models.FileField(_('Attachment'), upload_to='forum/attachments/', null=True, blank=True)

    class Meta:
        verbose_name = _('Forum Reply')
        verbose_name_plural = _('Forum Replies')
        ordering = ['created_at']

    def __str__(self):
        return f'Reply by {self.author} on {self.topic.title}'

    @property
    def like_count(self):
        return self.likes.filter(reply=self).count()


class ForumLike(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_likes'
    )
    topic = models.ForeignKey(ForumTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='likes')
    reply = models.ForeignKey(ForumReply, on_delete=models.SET_NULL, null=True, blank=True, related_name='likes')

    class Meta:
        unique_together = [('user', 'topic'), ('user', 'reply')]
