from django.contrib import admin
from listings.models import (
    District,
    Listing,
    ListingContact,
    ListingImage,
    ListingPromotion,
    ListingReport,
    ListingView,
    Region,
)

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingContactInline(admin.StackedInline):
    model = ListingContact
    extra = 0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    inlines = [ListingImageInline, ListingContactInline]
    list_display = (
        "id",
        "title",
        "slug",
        "listing_category",
        "user",
        "region",
        "district",
        "latitude",
        "longitude",
        "price",
        "currency",
        "is_negotiable",
        "has_delivery",
        "status",
        "published_at",
        "created_at",
    )
    search_fields = (
        "title",
        "slug",
        "description",
        "address",
        "landmark",
        "contact_name",
        "contact_phone",
        "user__username",
        "listing_category__name",
        "region__name",
        "district__name",
    )
    ordering = ("-created_at",)
    list_filter = (
        "status",
        "condition",
        "currency",
        "is_negotiable",
        "has_delivery",
        "region",
        "district",
        "listing_category",
        "created_at",
    )


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "is_main", "sort_order")
    search_fields = ("listing__title",)
    ordering = ("-id",)
    list_filter = ("is_main",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "type", "is_active", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    list_filter = ("type", "is_active", "created_at")
    prepopulated_fields = {"slug":('name',)}


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "region", "is_active", "created_at")
    search_fields = ("name", "slug", "region__name")
    ordering = ("region__name", "name")
    list_filter = ("region", "is_active", "created_at")
    prepopulated_fields = {"slug":('name',)}


@admin.register(ListingContact)
class ListingContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "contact_name",
        "phone_number",
        "allow_chat",
        "allow_call",
        "allow_telegram",
        "created_at",
    )
    search_fields = ("listing__title", "contact_name", "phone_number")
    ordering = ("-created_at",)
    list_filter = ("allow_chat", "allow_call", "allow_telegram", "created_at")


@admin.register(ListingPromotion)
class ListingPromotionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "promotion_type",
        "starts_at",
        "ends_at",
        "is_active",
        "created_at",
    )
    search_fields = ("listing__title",)
    ordering = ("-created_at",)
    list_filter = ("promotion_type", "is_active", "starts_at", "ends_at")


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "reporter",
        "reason",
        "status",
        "created_at",
    )
    search_fields = ("listing__title", "reporter__username", "reason", "comment")
    ordering = ("-created_at",)
    list_filter = ("status", "created_at")


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "session_key", "created_at")
    search_fields = ("listing__title", "user__username", "session_key")
    ordering = ("-created_at",)
    list_filter = ("created_at",)
