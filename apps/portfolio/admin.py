from django.contrib import admin
from django.utils import timezone
from .models import Portfolio, PortfolioItem

class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 0
    fields = ('item_type', 'title', 'file', 'rating', 'teacher_feedback')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public', 'created_at')
    inlines = [PortfolioItemInline]

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_user', 'item_type', 'has_file', 'rating', 'rated_by', 'rated_at', 'created_at')
    list_filter = ('item_type', 'rating')
    search_fields = ('title', 'portfolio__user__email')
    readonly_fields = ('rated_by', 'rated_at')

    @admin.display(description='User', ordering='portfolio__user')
    def get_user(self, obj):
        return obj.portfolio.user

    @admin.display(description='File', boolean=True)
    def has_file(self, obj):
        return bool(obj.file)

    def save_model(self, request, obj, form, change):
        if 'rating' in form.changed_data and obj.rating:
            obj.rated_by = request.user
            obj.rated_at = timezone.now()
        super().save_model(request, obj, form, change)
