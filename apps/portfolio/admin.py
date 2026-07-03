from django.contrib import admin
from .models import Portfolio, PortfolioItem

class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 0

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public', 'created_at')
    inlines = [PortfolioItemInline]
