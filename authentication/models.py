from django.db import models
from django.utils import timezone
from datetime import timedelta
from utils.models import BaseModel

class Purpose(models.TextChoices):
    REGISTER = "register", "Register"
    LOGIN = "login", "Login"
    RESET_PASSWORD = "reset_password", "Reset Password"

class OTPCode(BaseModel):
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices
    )
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def get_expiry():
        return timezone.now() + timedelta(minutes=3)

    def __str__(self):
        return self.code

class Step(models.IntegerChoices):
    AUTH = 1
    VERIFY = 2
    PROFILE = 3
    AVATAR = 4
    COMPLETED = 5

class RegistrationSession(BaseModel):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="registration_session"
    )
    current_step = models.IntegerField(
        choices=Step.choices,
        default=Step.AUTH
    )
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"User Registration session: {self.user.username} Current step: {self.current_step} | Is completed: {self.is_completed}"