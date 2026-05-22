from django.urls import path
from .views import (
    DistrictsListAPIView,
    ListingListAPIView,
    ListingDetailView,
    ListingCreateAPIView,
    RegionsListAPIView,
)

urlpatterns = [
    path("", ListingListAPIView.as_view()),
    path("<uuid:uuid>/", ListingDetailView.as_view()),
    path("create/", ListingCreateAPIView.as_view()),
    path("regions/", RegionsListAPIView.as_view()),
    path("regions/<slug:slug>/districts/", DistrictsListAPIView.as_view()),
]
