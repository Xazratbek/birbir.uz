from django.contrib.auth import authenticate
from rest_framework import serializers
from django.db.models import Q
from accounts.models import User
from accounts.serializers import ProfileSerializer
from authentication.models import RegistrationSession

class StartRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        if not email and not phone:
            raise serializers.ValidationError("Email yoki phone number kiritish majburiy")
        if email and phone:
            raise serializers.ValidationError("Faqat bittasi yuborilishi kerak")

        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    code = serializers.CharField(max_length=6)

class CompleteProfileSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    full_name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username band")
        return value

class UploadAvatarSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    avatar = serializers.ImageField(required=False, allow_null=True)

class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        user_obj = User.objects.filter(
            Q(username=login) | Q(email=login) | Q(phone_number=login)
        ).first()
        if user_obj:
            user = authenticate(username=user_obj.username, password=password)
        else:
            user = None
        if not user:
            raise serializers.ValidationError("Login yoki parol noto'g'ri")
        attrs["user"] = user
        return attrs


class RegistrationSessionSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = RegistrationSession
        fields = ("id", "current_step", "is_completed", "user")
