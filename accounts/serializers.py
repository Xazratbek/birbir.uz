from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import SellerApplication, SellerApplicationStatus, SellerFollow, SellerProfile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "bio", "avatar")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "avatar", "bio")


class SellerProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    active_listing_count = serializers.IntegerField(read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    bio = serializers.CharField(source="user.bio", read_only=True)
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = SellerProfile
        fields = [
            "user_id",
            "display_name",
            "avatar",
            "bio",
            "is_verified",
            "is_store",
            "telegram_username",
            "phone_visible",
            "reply_time_minutes",
            "active_listing_count",
            "followers_count",
        ]


class SellerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerApplication
        fields = ("business_name", "contact_phone", "business_description", "telegram_username", "is_store")

    def validate(self, attrs):
        request = self.context.get("request")
        if request and hasattr(request.user, "seller_application"):
            current = request.user.seller_application
            if current.status == SellerApplicationStatus.PENDING:
                raise ValidationError("Sizning arizangiz ko'rib chiqilmoqda")
            if current.status == SellerApplicationStatus.APPROVED:
                raise ValidationError("Siz allaqachon tasdiqlangan sellersiz")
        return attrs


class SellerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerApplication
        fields = (
            "id",
            "status",
            "business_name",
            "contact_phone",
            "business_description",
            "telegram_username",
            "is_store",
            "reviewed_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        )


class SellerFollowSerializer(serializers.Serializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, attrs):
        seller = attrs["seller"]
        user = self.context["request"].user
        if seller == user:
            raise ValidationError("O'z o'ziga obuna bo'lish mumkin emas")
        if not hasattr(seller, "seller_profile"):
            raise ValidationError("Bu foydalanuvchi sotuvchi emas")
        return attrs


class SellerApplicationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[SellerApplicationStatus.APPROVED, SellerApplicationStatus.REJECTED])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == SellerApplicationStatus.REJECTED and not attrs.get("rejection_reason"):
            raise ValidationError({"rejection_reason": "Rad etilganda sabab majburiy"})
        return attrs
