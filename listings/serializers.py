from rest_framework import serializers
from django.db import transaction
from django.utils.text import slugify
from .models import Listing, ListingContact, ListingImage, Region, District
from categories.models import Category
from categories.serializers import CategorySerializer
from accounts.serializers import UserSerializer

class RegionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'type','is_active']

class DistrictListSerializer(serializers.ModelSerializer):
    region = RegionListSerializer()
    class Meta:
        model = District
        fields = ['id', 'name', 'slug', 'type','region']

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
    views = serializers.SerializerMethodField()
    region = RegionListSerializer()
    district = DistrictListSerializer()

    def get_view_count(self, obj):
        return obj.views.count()

    class Meta:
        model = Listing
        fields = ['id','title','description','price','currency','listing_category','user','condition','latitude','longitude','status','views','address','has_delivery','contact_name','contact_phone','is_negotiable','published_at','expires_at','region','district','images']

class ListingCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.ChoiceField(choices=Listing._meta.get_field("currency").choices)
    category_id = serializers.UUIDField()
    latitude = serializers.DecimalField(max_digits=15, decimal_places=12)
    longitude = serializers.DecimalField(max_digits=15, decimal_places=12)
    address = serializers.CharField(max_length=255, allow_blank=True, required=False)
    landmark = serializers.CharField(max_length=255, allow_blank=True, required=False)
    contact_name = serializers.CharField(max_length=120, allow_blank=True, required=False)
    contact_phone = serializers.CharField(max_length=20, allow_blank=True, required=False)
    allow_chat = serializers.BooleanField(required=False, default=True)
    allow_call = serializers.BooleanField(required=False, default=False)
    allow_telegram = serializers.BooleanField(required=False, default=False)
    has_delivery = serializers.BooleanField(required=False, default=False)
    is_negotiable = serializers.BooleanField(required=False, default=False)
    condition = serializers.CharField(required=True)
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000,allow_empty_file=True,use_url=False,write_only=True)
    )

    def validate(self, attrs):
        if not (attrs.get("allow_chat") or attrs.get("allow_call") or attrs.get("allow_telegram")):
            raise serializers.ValidationError("Kamida bitta aloqa usuli tanlanishi kerak.")
        return attrs
