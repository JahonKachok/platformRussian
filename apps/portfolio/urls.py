from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.PortfolioView.as_view(), name='view'),
    path('edit/', views.PortfolioEditView.as_view(), name='edit'),
    path('item/add/', views.PortfolioItemAddView.as_view(), name='item-add'),
    path('item/<int:pk>/delete/', views.PortfolioItemDeleteView.as_view(), name='item-delete'),
    path('download/', views.PortfolioPDFView.as_view(), name='download-pdf'),
    path('review/', views.AdminPortfolioReviewListView.as_view(), name='admin-review'),
    path('review/<int:pk>/rate/', views.AdminPortfolioRateView.as_view(), name='admin-rate'),
]
