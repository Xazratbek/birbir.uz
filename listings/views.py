from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import DistrictListSerializer, ListingListSerializer, ListingDetailSerializer, ListingCreateSerializer, RegionListSerializer
from .models import District, Listing, Region, RegionTypeChoice, ListingView
from .pagination import ListingPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Listing, ListingContact, ListingImage, Region, District
from categories.models import Category
from .utils import get_location_details
from django.db.models import Prefetch, F, Count
from .tasks import singleton_task, oddy_task

class ListingListAPIView(ListAPIView):
    serializer_class = ListingListSerializer
    queryset = Listing.objects.all().order_by('-created_at').prefetch_related('images')
    pagination_class = ListingPagination

    def get_queryset(self):
        oddy_task.delay()
        return super().get_queryset()

class ListingDetailView(RetrieveAPIView):
    serializer_class = ListingDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'uuid'

    def get_object(self):
        listing = Listing.objects.filter(id=self.kwargs.get('uuid')).select_related('region','district','listing_category').prefetch_related('images','views').first()
        singleton_task.delay(listing.id)
        if self.request.user.is_authenticated:
            ListingView.objects.get_or_create(listing=listing,user=self.request.user,session_key=None)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key
            ListingView.objects.get_or_create(listing=listing,user=None,session_key=session_key)
        return listing

class ListingCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ListingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = serializer.validated_data.pop('images','')
        allow_chat = serializer.validated_data.pop('allow_chat')
        allow_call = serializer.validated_data.pop('allow_call')
        allow_telegram = serializer.validated_data.pop('allow_telegram')
        category_id = serializer.validated_data.pop('category_id')
        latitude = serializer.validated_data.pop('latitude')
        longitude = serializer.validated_data.pop('longitude')
        address = serializer.validated_data.pop('address')

        with transaction.atomic():
            lakatsiya = get_location_details(lat=latitude,lon=longitude)
            print(lakatsiya)
            if lakatsiya.get('district') is None:
                region, created = Region.objects.get_or_create(name=lakatsiya.get('region'),type=RegionTypeChoice.CITY)

            elif lakatsiya.get('region') is None:
                region, created = Region.objects.get_or_create(name=lakatsiya.get('district'))

            if lakatsiya.get('district') is not None:
                district, created = District.objects.get_or_create(
                    name=lakatsiya.get('district'),
                    region=region,
                )
            else:
                district, created = District.objects.get_or_create(
                    name=lakatsiya.get('city'),
                    region=region,
                )

            category = get_object_or_404(Category,pk=category_id)
            elon = Listing.objects.create(user=request.user,listing_category=category,region=region,district=district,address=address if address else lakatsiya.get('full_address'),**serializer.validated_data)

            rasmlar = []
            for i,image in enumerate(images):
                if i == 0:
                    rasmlar.append(ListingImage(listing=elon,image=image,is_main=True,sort_order=0))
                rasmlar.append(ListingImage(listing=elon,image=image,is_main=False,sort_order=0))

            ListingImage.objects.bulk_create(rasmlar)
            ListingContact.objects.create(listing=elon,phone_number=elon.contact_phone,contact_name=elon.contact_name,allow_chat=allow_chat,allow_call=allow_call,allow_telegram=allow_telegram)


        return Response({
            "status":status.HTTP_201_CREATED,
            "message":  "E'lon qo'shildi",
            "elon": ListingListSerializer(elon).data
        },status=status.HTTP_201_CREATED)


class RegionsListAPIView(ListAPIView):
    serializer_class = RegionListSerializer
    queryset = Region.objects.all()


class DistrictsListAPIView(ListAPIView):
    serializer_class = DistrictListSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')

        return District.objects.filter(
            region__slug=slug
        )
