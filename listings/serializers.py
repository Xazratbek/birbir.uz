from rest_framework import serializers
from .models import District, Listing, ListingImage, Region
from categories.serializers import CategorySerializer
from accounts.serializers import UserSerializer

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id','listing','image','is_main']

class ListingListSerializer(serializers.ModelSerializer):
    condition = serializers.CharField(source='get_condition_display', read_only=True)
    currency = serializers.CharField(source='get_currency_display',read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id','title','price','condition','currency','images','created_at']


class ListingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing_category = CategorySerializer()
    images = ListingImageSerializer(many=True, read_only=True)
    condition = serializers.CharField(source='get_condition_display', read_only=True)
    currency = serializers.CharField(source='get_currency_display',read_only=True)
    status = serializers.CharField(source='get_status_display',read_only=True)
    view_count = serializers.SerializerMethodField()

    def get_view_count(self, obj):
        return obj.views.count()

    class Meta:
        model = Listing
        fields = ['id','title','description','price','currency','listing_category','user','condition','latitude','longitude','status','view_count','images']

class ListingCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.CharField(required=True,write_only=True)
    longitude = serializers.CharField(required=True,write_only=True)

    class Meta:
        model = Listing
        fields = ['title','description','price','currency','listing_category','condition','latitude','longitude']

class RegionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'type']

class DistrictListSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'slug', 'region']

