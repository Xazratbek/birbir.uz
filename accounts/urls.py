from django.urls import path
from .views import ProfileUpdateView

urlpatterns = [
    path('profile/update/<uuid:uuid>/',ProfileUpdateView.as_view())
]
