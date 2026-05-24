from rest_framework.permissions import IsAuthenticated
from authentication.serializers import ProfileSerializer
from .serializers import UserSerializer, SellerProfileSerializer, SellerFollowSerializer
from .models import User, SellerProfile, SellerFollow
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.views import APIView
from .permissions import IsSellerProfileOwner, IsProfileOwner
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q

class ProfileUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsProfileOwner]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'uuid'

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

class SellerProfilesView(ListAPIView):
    queryset = SellerProfile.objects.all().select_related('user')
    serializer_class = SellerProfileSerializer

class SellerProfileDetailView(RetrieveAPIView):
    serializer_class = SellerProfileSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return SellerProfile.objects.all().select_related('user').annotate(followers_count=Count('seller_followers',distinct=True),active_listing_count=Count('user__user_listings',filter=Q(status='active'),distinct=True))

class SellerProfileUpdate(UpdateAPIView):
    permission_classes = [IsSellerProfileOwner]
    queryset = SellerProfile.objects.all().select_related('user')
    serializer_class = SellerProfileSerializer

class SellerFollowOrDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,pk):
        serializer = SellerFollowSerializer(data=request.data,context={"request":request})
        serializer.is_valid(raise_exception=True)
        follow, created = SellerFollow.objects.get_or_create(follower=request.user)
        if not created:
            follow.objects.delete()
            follow.save()

        return Response({
            "status":status.HTTP_200_OK,
            "message":f"Obuna {'bo\'ldingiz' if created else 'bekor qilindi'}",
        },status=status.HTTP_200_OK)