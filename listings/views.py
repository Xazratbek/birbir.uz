from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import DistrictListSerializer, ListingListSerializer, ListingDetailSerializer, ListingCreateSerializer, RegionListSerializer
from .models import District, Listing, Region
from .pagination import ListingPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class ListingListAPIView(ListAPIView):
    serializer_class = ListingListSerializer
    queryset = Listing.objects.all().order_by('-created_at')
    pagination_class = ListingPagination

class ListingDetailView(RetrieveAPIView):
    serializer_class = ListingDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return Listing.objects.all()

class ListingCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ListingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # elon = serializer.save(user=request.user)
        return Response({
            "status":status.HTTP_201_CREATED,
            "message":"Yangi e'lon qo'shildi"
        })
    

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