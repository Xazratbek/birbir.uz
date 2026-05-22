from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from authentication.views import *

urlpatterns = [
    path("signup/start/", StartSignupView.as_view()),
    path("signup/verify/", VerifySignupOTPView.as_view()),
    path("signup/profile/", CompleteProfileView.as_view()),
    path("signup/avatar/", UploadAvatarView.as_view()),
    path("signup/session/<uuid:session_id>/", RegistrationSessionDetailView.as_view()),
    path('signup/resendcode/',ResendCodeView.as_view()),
    path("login/", LoginView.as_view()),
    path("me/", ProfileView.as_view()),
    path('logout/',TokenBlacklistView.as_view())
]
