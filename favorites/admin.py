from django.contrib import admin
from favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "favorite_listing", "created_at")
    search_fields = ("user__username", "user__email", "favorite_listing__title")
    ordering = ("-created_at",)
    list_filter = ("created_at", "updated_at")
