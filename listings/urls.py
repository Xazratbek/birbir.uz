from django.urls import path
from .views import ListingListAPIView, ListingDetailView, ListingCreateAPIView

urlpatterns = [
    path('',ListingListAPIView.as_view()),
    path('<uuid:uuid>/',ListingDetailView.as_view()),
    path('create/',ListingCreateAPIView.as_view())
]
