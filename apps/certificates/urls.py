from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.CertificateListView.as_view(), name='list'),
    path('<uuid:certificate_id>/', views.CertificateDetailView.as_view(), name='detail'),
    path('verify/<uuid:certificate_id>/', views.CertificateVerifyView.as_view(), name='verify'),
    path('<uuid:certificate_id>/download/', views.CertificateDownloadView.as_view(), name='download'),
]
