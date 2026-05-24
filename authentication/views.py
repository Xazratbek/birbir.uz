from django.core.mail import send_mail
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import AuthType, User
from authentication.models import OTPCode, Purpose, RegistrationSession, Step
from authentication.serializers import *
from authentication.utils import generate_otp, generate_password, generate_username, send_sms

class StartSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StartRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        phone_number = serializer.validated_data.get("phone_number")
        print(email,phone_number)
        otp = generate_otp()

        with transaction.atomic():
            user = User.objects.create_user(
                username=generate_username(),
                password=generate_password(),
                email=email if email else None,
                phone_number=phone_number if phone_number else None,
                auth_type=AuthType.EMAIL if email else AuthType.PHONE,
            )
            session = RegistrationSession.objects.create(user=user, current_step=Step.VERIFY)
            OTPCode.objects.create(
                email=email,
                phone_number=phone_number,
                code=otp,
                purpose=Purpose.REGISTER,
                expires_at=OTPCode.get_expiry(),
            )

        if email:
            send_mail("Tasdiqlash kodi", f"Sizning kod: {otp}", 'xazratbek123@gmail.com', [email], fail_silently=False)
        else:
            send_sms(phone_number, f"Tasdiqlash kodi: {otp}")

        return Response({"status":status.HTTP_200_OK,"session_id": str(session.id), "step": Step.VERIFY,"message":f"{email if email else phone_number}-ga tasdiqlash kodi yuborildi"}, status=status.HTTP_201_CREATED)

class ResendCodeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        session_id = request.data.get('session_id','')
        if session_id:
            session = RegistrationSession.objects.filter(id=session_id).select_related('user').first()
            if session and not (session.user.is_phone_verified or session.user.is_email_verified) and session.current_step == Step.VERIFY:
                email = session.user.email
                phone_number = session.user.phone_number
                otp = generate_otp()
                OTPCode.objects.create(
                                email=email if email else None,
                                phone_number=phone_number if phone_number else None,
                                code=otp,
                                purpose=Purpose.REGISTER,
                                expires_at=OTPCode.get_expiry(),
                            )
                if session.user.email:
                    send_mail("Tasdiqlash kodi", f"Sizning kod: {otp}", 'xazratbek123@gmail.com', [session.user.email], fail_silently=False)
                else:
                    send_sms(session.user.phone_number, f"Tasdiqlash kodi: {otp}")

                return Response({"status":status.HTTP_201_CREATED,"session_id": str(session.id), "step": Step.VERIFY,"message":f"{email if email else phone_number}-ga tasdiqlash kodi qayta yuborildi"}, status=status.HTTP_201_CREATED)

        return Response({
            "status":status.HTTP_404_NOT_FOUND,
            "message":"session topilmadi"
        },status=status.HTTP_404_NOT_FOUND)


class VerifySignupOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = RegistrationSession.objects.select_related("user").filter(id=serializer.validated_data["session_id"]).first()
        if not session:
            return Response({'status':status.HTTP_404_NOT_FOUND,"detail": "Session topilmadi"}, status=404)

        user = session.user
        otp = OTPCode.objects.filter(
            purpose=Purpose.REGISTER,
            is_used=False,
            email=user.email if user.email else None,
            phone_number=user.phone_number if user.phone_number else None,
        ).order_by("-created_at").first()

        if not otp or otp.is_expired() or otp.code != serializer.validated_data["code"]:
            return Response({"status":status.HTTP_400_BAD_REQUEST,"detail": "Kod noto'g'ri yoki eskirgan"}, status=400)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        if user.email:
            user.is_email_verified = True

        if user.phone_number:
            user.is_phone_verified = True

        user.save(update_fields=["is_email_verified", "is_phone_verified", "updated_at"])

        session.current_step = Step.PROFILE
        session.save(update_fields=["current_step", "updated_at"])

        return Response({"status":status.HTTP_200_OK,"message":"Code tasdiqlandi","step": Step.PROFILE})


class CompleteProfileView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompleteProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = RegistrationSession.objects.select_related("user").filter(id=serializer.validated_data["session_id"]).first()
        if not session:
            return Response({"detail": "Session topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        user = session.user
        user.first_name = serializer.validated_data["full_name"]
        user.username = serializer.validated_data["username"]
        user.bio = serializer.validated_data.get("bio", "")
        user.set_password(serializer.validated_data["password"])
        user.save()

        session.current_step = Step.AVATAR
        session.save(update_fields=["current_step", "updated_at"])

        return Response({"step": Step.AVATAR})


class UploadAvatarView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UploadAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = RegistrationSession.objects.select_related("user").filter(id=serializer.validated_data["session_id"]).first()
        if not session:
            return Response({"detail": "Session topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        avatar = serializer.validated_data.get("avatar")
        if avatar:
            session.user.avatar = avatar
            session.user.save(update_fields=["avatar", "updated_at"])

        session.current_step = Step.COMPLETED
        session.is_completed = True
        session.save(update_fields=["current_step", "is_completed", "updated_at"])

        return Response({'status':status.HTTP_200_OK,"step": Step.COMPLETED, "profile": ProfileSerializer(session.user).data},status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": ProfileSerializer(user).data,
        })

class RegistrationSessionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        session = RegistrationSession.objects.select_related("user").filter(id=session_id).first()
        if not session:
            return Response({"detail": "Session topilmadi"}, status=404)
        return Response(RegistrationSessionSerializer(session).data)
