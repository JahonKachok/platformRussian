from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.PortfolioView.as_view(), name='view'),
    path('edit/', views.PortfolioEditView.as_view(), name='edit'),
    path('item/add/', views.PortfolioItemAddView.as_view(), name='item-add'),
    path('item/<int:pk>/delete/', views.PortfolioItemDeleteView.as_view(), name='item-delete'),
    path('download/', views.PortfolioPDFView.as_view(), name='download-pdf'),
]
