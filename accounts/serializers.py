from rest_framework import serializers
from accounts.models import User, SellerProfile, SellerFollow
from rest_framework.exceptions import ValidationError

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "bio", "avatar")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "avatar", "bio")

class SellerProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField()
    active_listing_count = serializers.IntegerField()
    user_id = serializers.CharField(source='user.id')
    avatar = serializers.ImageField(source='user.avatar')
    bio = serializers.CharField(source='user.bio')
    is_verified = serializers.BooleanField(source='user.is_verified')

    class Meta:
        model = SellerProfile
        fields = [
            'user_id',
            'display_name',
            'avatar',
            'bio',
            'is_verified',
            'is_store',
            'telegram_username',
            'phone_visible',
            'reply_time_minutes',
            'active_listing_count',
            'followers_count',
        ]

class SellerFollowSerializer(serializers.Serializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=SellerProfile.objects.all(),read_only=True)

    class Meta:
        model = SellerFollow
        fields = ['seller']

    def validate_seller(self, value):
        seller = SellerProfile.objects.filter(pk=value).first()
        if seller:
            return value
        else:
            raise ValidationError("Sotuvchi topilmadi")

    def validate(self, attrs):
        seller = attrs['seller']
        user = self.context.get('request').user
        if seller == user:
            raise ValidationError("O'z o'ziga obuna bo'lish mumkin emas")
        return attrs