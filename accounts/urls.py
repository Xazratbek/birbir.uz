from django.urls import path

from .views import (
    ProfileUpdateView,
    ProfileView,
    SellerApplicationCreateView,
    SellerApplicationReviewView,
    SellerApplicationStatusView,
    SellerFollowOrDeleteAPI,
    SellerProfileDetailView,
    SellerProfileUpdate,
    SellerProfilesView,
)

urlpatterns = [
    path("profile/update/<uuid:uuid>/", ProfileUpdateView.as_view()),
    path("me/", ProfileView.as_view()),
    path("sellers/", SellerProfilesView.as_view()),
    path("sellers/<uuid:uuid>/", SellerProfileDetailView.as_view()),
    path("sellers/<uuid:pk>/follow-toggle/", SellerFollowOrDeleteAPI.as_view()),
    path("seller/profile/<uuid:pk>/", SellerProfileUpdate.as_view()),
    path("seller/apply/", SellerApplicationCreateView.as_view()),
    path("seller/application-status/", SellerApplicationStatusView.as_view()),
    path("seller/applications/<uuid:application_id>/review/", SellerApplicationReviewView.as_view()),
]
