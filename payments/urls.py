from django.urls import path
from .views import PaymentsPlaceholderView

urlpatterns = [
    path("", PaymentsPlaceholderView.as_view(), name="home"),
]
