from .models import Favorite
from .serializers import FavoriteListSerializer, FavoriteCreateSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView
from accounts.permissions import IsFavoriteOwner
from rest_framework import status
from rest_framework.response import Response
from .pagination import FavoritePagination

class FavoriteListAPIView(ListAPIView):
    serializer_class = FavoriteListSerializer
    permission_classes = [IsFavoriteOwner]
    pagination_class = FavoritePagination

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDelete(DestroyAPIView):
    permission_classes = [IsFavoriteOwner]
    serializer_class = FavoriteListSerializer
    queryset =  Favorite.objects.all()

class FavoriteCreateAPIView(CreateAPIView):
    permission_classes = [IsFavoriteOwner]
    serializer_class = FavoriteCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            favorite_listing=serializer.validated_data['favorite_listing']
        )

        if not created:
            favorite.delete()

        return Response({
            "status": status.HTTP_200_OK,
            "message": f"{'Saqlanganlarga qo\'shildi' if created else 'Saqlanganlardan olib tashlandi'}"
        }, status=status.HTTP_200_OK)
