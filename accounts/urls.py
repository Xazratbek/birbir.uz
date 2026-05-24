from django.urls import path
from .views import ProfileUpdateView, ProfileView

urlpatterns = [
    path('profile/update/<uuid:uuid>/',ProfileUpdateView.as_view()),
    path("me/", ProfileView.as_view()),
    path("me/", ProfileView.as_view()),
    path("me/", ProfileView.as_view()),
    path("me/", ProfileView.as_view()),
]
