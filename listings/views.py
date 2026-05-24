from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from categories.models import Category
from .models import *
from .pagination import ListingPagination
from .serializers import *
from .tasks import oddy_task, singleton_task
from .utils import get_location_details


class ListingListAPIView(ListAPIView):
    serializer_class = ListingListSerializer
    queryset = Listing.objects.all().order_by("-created_at").prefetch_related("images")
    pagination_class = ListingPagination

    def get_queryset(self):
        oddy_task.delay()
        return super().get_queryset()


class ListingDetailView(RetrieveAPIView):
    serializer_class = ListingDetailSerializer
    lookup_field = "id"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        return (
            Listing.objects.select_related("region", "district", "listing_category", "user", "contact")
            .prefetch_related("images", "views", "attribute_values__attribute", "attribute_values__option", "attribute_values__attribute__options")
            .annotate(total_views=Count("views"))
        )

    def get_object(self):
        listing = super().get_object()
        singleton_task.delay(str(listing.id))

        if self.request.user.is_authenticated:
            ListingView.objects.get_or_create(listing=listing, user=self.request.user, session_key=None)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key
            ListingView.objects.get_or_create(listing=listing, user=None, session_key=session_key)

        return listing


class ListingCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ListingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images = serializer.validated_data.pop("images")
        attributes = serializer.validated_data.pop("attributes", [])
        allow_chat = serializer.validated_data.pop("allow_chat")
        allow_call = serializer.validated_data.pop("allow_call")
        allow_telegram = serializer.validated_data.pop("allow_telegram")
        category_id = serializer.validated_data.pop("category_id")
        latitude = serializer.validated_data.pop("latitude")
        longitude = serializer.validated_data.pop("longitude")
        address = serializer.validated_data.pop("address", "")
        landmark = serializer.validated_data.pop("landmark", "")

        with transaction.atomic():
            location = get_location_details(lat=latitude, lon=longitude)

            region_name = location.get("region")
            district_name = location.get("district") or location.get("city")

            region = None
            district = None

            if region_name:
                region, _ = Region.objects.get_or_create(
                    name=region_name,
                    defaults={"type": RegionTypeChoice.CITY},
                )

            if district_name:
                if region is None:
                    region, _ = Region.objects.get_or_create(
                        name=district_name,
                        defaults={"type": RegionTypeChoice.CITY},
                    )
                district, _ = District.objects.get_or_create(
                    name=district_name,
                    region=region,
                )

            category = get_object_or_404(Category, pk=category_id)

            elon = Listing.objects.create(
                user=request.user,
                listing_category=category,
                region=region,
                district=district,
                address=address or location.get("full_address", ""),
                landmark=landmark,
                **serializer.validated_data,
            )

            listing_images = []
            for index, image in enumerate(images):
                listing_images.append(
                    ListingImage(
                        listing=elon,
                        image=image,
                        is_main=index == 0,
                        sort_order=index,
                    )
                )
            ListingImage.objects.bulk_create(listing_images)

            ListingContact.objects.create(
                listing=elon,
                phone_number=serializer.validated_data.get("contact_phone", ""),
                contact_name=serializer.validated_data.get("contact_name", ""),
                allow_chat=allow_chat,
                allow_call=allow_call,
                allow_telegram=allow_telegram,
            )

            attribute_map = {str(attr.id): attr for attr in category.attributes.filter(is_active=True).prefetch_related("options")}
            listing_attribute_values = []

            for item in attributes:
                attribute = attribute_map.get(str(item["attribute_id"]))
                if attribute is None:
                    continue

                option = None
                if item.get("option_id"):
                    option = attribute.options.filter(id=item["option_id"], is_active=True).first()

                listing_attribute_values.append(
                    ListingAttributeValue(
                        listing=elon,
                        attribute=attribute,
                        option=option,
                        value_text=item.get("value_text") or "",
                        value_int=item.get("value_int"),
                        value_decimal=item.get("value_decimal"),
                        value_bool=item.get("value_bool"),
                    )
                )

            ListingAttributeValue.objects.bulk_create(listing_attribute_values)

        elon = (
            Listing.objects.select_related("listing_category", "region", "district", "contact", "user")
            .prefetch_related("images", "attribute_values__attribute", "attribute_values__option")
            .get(id=elon.id)
        )

        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "E'lon qo'shildi",
                "elon": ListingDetailSerializer(elon).data,
            },
            status=status.HTTP_201_CREATED,
        )


class RegionsListAPIView(ListAPIView):
    serializer_class = RegionListSerializer
    queryset = Region.objects.all()


class DistrictsListAPIView(ListAPIView):
    serializer_class = DistrictListSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return District.objects.filter(region__slug=slug)
