import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


def avatar_upload(instance, filename):
    ext = filename.split('.')[-1]
    return f'uploads/avatars/{uuid.uuid4().hex}.{ext}'


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, _('Student')),
        (ROLE_TEACHER, _('Teacher')),
        (ROLE_ADMIN, _('Admin')),
    ]

    email = models.EmailField(_('Email'), unique=True)
    role = models.CharField(_('Role'), max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    avatar = models.ImageField(_('Avatar'), upload_to=avatar_upload, null=True, blank=True)
    bio = models.TextField(_('Bio'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('Date of birth'), null=True, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    language = models.CharField(_('Preferred language'), max_length=10, default='uz')
    email_verified = models.BooleanField(_('Email verified'), default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    last_active = models.DateTimeField(_('Last active'), null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'accounts_user'

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return f'/static/images/svg/default-avatar.svg'

    def get_initials(self):
        name = self.get_full_name()
        if name:
            parts = name.split()
            return ''.join(p[0].upper() for p in parts[:2])
        return self.email[0].upper()
