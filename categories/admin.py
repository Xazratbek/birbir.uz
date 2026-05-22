from django.contrib import admin
from categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent", "created_at")
    search_fields = ("name", "slug", "parent__name")
    ordering = ("name",)
    list_filter = ("created_at", "updated_at")
    prepopulated_fields = {"slug":('name',)}