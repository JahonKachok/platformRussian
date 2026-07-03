from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from .models import Certificate
from .services import issue_certificate


class CertificateListView(LoginRequiredMixin, ListView):
    model = Certificate
    template_name = 'certificates/list.html'
    context_object_name = 'certificates'

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user, is_valid=True).select_related('course')


class CertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = 'certificates/detail.html'
    context_object_name = 'certificate'
    slug_field = 'certificate_id'
    slug_url_kwarg = 'certificate_id'


class CertificateVerifyView(TemplateView):
    template_name = 'certificates/verify.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            cert = Certificate.objects.select_related('user', 'course').get(
                certificate_id=kwargs['certificate_id']
            )
            ctx['certificate'] = cert
            ctx['is_valid'] = cert.is_valid
        except Certificate.DoesNotExist:
            ctx['certificate'] = None
            ctx['is_valid'] = False
        return ctx


class CertificateDownloadView(LoginRequiredMixin, View):
    def get(self, request, certificate_id):
        cert = get_object_or_404(Certificate, certificate_id=certificate_id, user=request.user)
        if not cert.pdf_file:
            cert = issue_certificate(request.user, cert.course)
        if cert.pdf_file:
            return FileResponse(cert.pdf_file.open('rb'), content_type='application/pdf',
                                as_attachment=True, filename=f'certificate_{cert.short_id}.pdf')
        raise Http404
