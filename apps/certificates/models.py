import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Certificate(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='certificates'
    )
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user} - {self.course.title}'

    @property
    def verification_url(self):
        return f'/certificates/verify/{self.certificate_id}/'

    @property
    def short_id(self):
        return str(self.certificate_id)[:8].upper()
