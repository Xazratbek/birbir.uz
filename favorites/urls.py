from django.urls import path
from .views import FavoriteListAPIView, FavoriteDelete,FavoriteCreateAPIView

urlpatterns = [
    path('',FavoriteListAPIView.as_view()),
    path('create/',FavoriteCreateAPIView.as_view()),
    path('delete/',FavoriteDelete.as_view())
]
