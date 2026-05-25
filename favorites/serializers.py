from rest_framework import serializers
from .models import Favorite
from accounts.serializers import UserSerializer
from listings.serializers import ListingListSerializer
from listings.models import Listing

class FavoriteListSerializer(serializers.ModelSerializer):
    favorite_listing = ListingListSerializer(read_only=True)
    class Meta:
        model = Favorite
        fields = ['id','favorite_listing']

class FavoriteCreateSerializer(serializers.ModelSerializer):
    favorite_listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())
    class Meta:
        model = Favorite
        fields = ['favorite_listing']