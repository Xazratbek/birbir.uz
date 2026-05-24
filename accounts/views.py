from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.serializers import ProfileSerializer
from .models import SellerApplication, SellerApplicationStatus, SellerFollow, SellerProfile, User
from .permissions import IsProfileOwner, IsSellerProfileOwner
from .serializers import (
    SellerApplicationCreateSerializer,
    SellerApplicationReviewSerializer,
    SellerApplicationSerializer,
    SellerFollowSerializer,
    SellerProfileSerializer,
    UserSerializer,
)


class ProfileUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsProfileOwner]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "uuid"


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)


class SellerProfilesView(ListAPIView):
    queryset = SellerProfile.objects.all().select_related("user")
    serializer_class = SellerProfileSerializer


class SellerProfileDetailView(RetrieveAPIView):
    serializer_class = SellerProfileSerializer
    lookup_field = "id"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        return SellerProfile.objects.all().select_related("user").annotate(
            followers_count=Count("user__seller_followers", distinct=True),
            active_listing_count=Count("user__user_listings", filter=Q(user__user_listings__status="active"), distinct=True),
        )


class SellerProfileUpdate(UpdateAPIView):
    permission_classes = [IsSellerProfileOwner]
    queryset = SellerProfile.objects.all().select_related("user")
    serializer_class = SellerProfileSerializer


class SellerApplicationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SellerApplicationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        application, _ = SellerApplication.objects.update_or_create(
            user=request.user,
            defaults={
                **serializer.validated_data,
                "status": SellerApplicationStatus.PENDING,
                "rejection_reason": "",
                "reviewed_by": None,
                "reviewed_at": None,
            },
        )
        return Response(SellerApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class SellerApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        application = SellerApplication.objects.filter(user=request.user).first()
        if not application:
            return Response({"detail": "Seller arizasi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        return Response(SellerApplicationSerializer(application).data)


class SellerApplicationReviewView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, application_id):
        application = SellerApplication.objects.select_related("user").filter(id=application_id).first()
        if not application:
            return Response({"detail": "Ariza topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SellerApplicationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data["status"]

        application.status = status_value
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.rejection_reason = serializer.validated_data.get("rejection_reason", "")
        application.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])

        if status_value == SellerApplicationStatus.APPROVED:
            SellerProfile.objects.get_or_create(
                user=application.user,
                defaults={
                    "display_name": application.business_name,
                    "is_store": application.is_store,
                    "telegram_username": application.telegram_username,
                },
            )

        return Response(SellerApplicationSerializer(application).data)


class SellerFollowOrDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = SellerFollowSerializer(data={"seller": pk}, context={"request": request})
        serializer.is_valid(raise_exception=True)

        seller = serializer.validated_data["seller"]
        follow, created = SellerFollow.objects.get_or_create(follower=request.user, seller=seller)
        if not created:
            follow.delete()

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": f"Obuna {'bo\'ldingiz' if created else 'bekor qilindi'}",
            },
            status=status.HTTP_200_OK,
        )
