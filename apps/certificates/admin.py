from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_id', 'issued_at', 'is_valid')
    list_filter = ('is_valid',)
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('certificate_id', 'issued_at')
