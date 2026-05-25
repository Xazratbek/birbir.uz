from django.contrib import admin

from accounts.models import SellerApplication, SellerFollow, SellerProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "username",
        "email",
        "phone_number",
        "auth_type",
        "is_email_verified",
        "is_phone_verified",
        "is_verified",
        "created_at",
    )
    search_fields = ("username", "email", "phone_number")
    ordering = ("-created_at",)
    list_filter = ("auth_type", "is_email_verified", "is_phone_verified", "is_verified", "created_at")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "display_name",
        "is_store",
        "phone_visible",
        "reply_time_minutes",
        "active_listing_count",
        "created_at",
    )
    search_fields = ("display_name", "user__username", "user__email", "telegram_username")
    ordering = ("-created_at",)
    list_filter = ("is_store", "phone_visible", "created_at")


@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "business_name", "status", "reviewed_by", "reviewed_at", "created_at")
    search_fields = ("user__username", "user__email", "business_name", "contact_phone")
    list_filter = ("status", "is_store", "created_at")
    ordering = ("-created_at",)


@admin.register(SellerFollow)
class SellerFollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "seller", "created_at")
    search_fields = (
        "follower__username",
        "follower__email",
        "seller__username",
        "seller__email",
    )
    ordering = ("-created_at",)
    list_filter = ("created_at",)
