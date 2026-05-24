from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from utils.models import BaseModel


class CustomUserManager(UserManager):
    @classmethod
    def normalize_email(cls, email):
        if email in (None, ""):
            return None
        return super().normalize_email(email)


class AuthType(models.TextChoices):
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"


class SellerApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    auth_type = models.CharField(
        max_length=10,
        choices=AuthType.choices
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    objects = CustomUserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class SellerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    display_name = models.CharField(max_length=150)
    is_store = models.BooleanField(default=False)
    telegram_username = models.CharField(max_length=100, blank=True)
    phone_visible = models.BooleanField(default=True)
    reply_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    active_listing_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.display_name

    class Meta:
        db_table = "seller_profiles"
        verbose_name = "Sotuvchi profili"
        verbose_name_plural = "Sotuvchi profillari"


class SellerApplication(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_application")
    status = models.CharField(max_length=20, choices=SellerApplicationStatus.choices, default=SellerApplicationStatus.PENDING)
    business_name = models.CharField(max_length=180)
    contact_phone = models.CharField(max_length=20)
    business_description = models.TextField(blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    is_store = models.BooleanField(default=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_seller_applications")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    class Meta:
        db_table = "seller_applications"
        verbose_name = "Sotuvchi arizasi"
        verbose_name_plural = "Sotuvchi arizalari"


class SellerFollow(BaseModel):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_sellers")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_followers")

    def __str__(self):
        return f"{self.follower.username} -> {self.seller.username}"

    class Meta:
        db_table = "seller_follows"
        verbose_name = "Sotuvchiga obuna"
        verbose_name_plural = "Sotuvchiga obunalar"
        constraints = [
            models.UniqueConstraint(fields=["follower", "seller"], name="unique_seller_follow")
        ]
