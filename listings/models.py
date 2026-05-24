from django.urls import reverse
from utils.models import BaseModel
from categories.models import Category
from accounts.models import User
from django.db import models
from django.utils.text import slugify

class ConditionChoice(models.TextChoices):
    NEW = "new", "Yangi"
    USED = "used", "B/U"

class StatusChoice(models.TextChoices):
    ACTIVE = "active", "Faol"
    SOLD = "sold", "Sotilgan"
    ARCHIVED = "archived", "Arxivlangan"
    DELETED = "deleted","O'chirilgan"

class CurrencyChoice(models.TextChoices):
    UZS = 'uzs', "So'm"
    USD = 'usd', "USD"
    EUR = "eur", "Euro"

class RegionTypeChoice(models.TextChoices):
    CITY = "city", "Shahar"
    REGION = "region", "Viloyat"

class ReportStatusChoice(models.TextChoices):
    NEW = "new", "Yangi"
    REVIEWED = "reviewed", "Ko'rilgan"
    REJECTED = "rejected", "Rad etilgan"
    RESOLVED = "resolved", "Hal qilingan"

class PromotionTypeChoice(models.TextChoices):
    TOP = "top", "Top"
    URGENT = "urgent", "Shoshilinch"
    PRO = "pro", "Pro"
    HIGHLIGHT = "highlight", "Ajratilgan"


class AttributeValueTypeChoice(models.TextChoices):
    TEXT = "text", "Matn"
    INTEGER = "integer", "Butun son"
    DECIMAL = "decimal", "Kasr son"
    BOOLEAN = "boolean", "Ha/Yo'q"
    SELECT = "select", "Tanlov"


class CategoryAttribute(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="attributes")
    key = models.SlugField(max_length=120)
    label = models.CharField(max_length=150)
    value_type = models.CharField(max_length=20, choices=AttributeValueTypeChoice.choices)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=False)
    unit = models.CharField(max_length=30, blank=True, default="")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.name} | {self.label}"

    class Meta:
        db_table = "category_attributes"
        verbose_name = "Kategoriya atributi"
        verbose_name_plural = "Kategoriya atributlari"
        constraints = [
            models.UniqueConstraint(fields=["category", "key"], name="unique_category_attribute_key"),
        ]
        indexes = [
            models.Index(fields=["category", "is_active", "sort_order"], name="cat_attr_active_sort_idx"),
            models.Index(fields=["category", "is_required"], name="cat_attr_required_idx"),
        ]


class CategoryAttributeOption(BaseModel):
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name="options")
    value = models.SlugField(max_length=120)
    label = models.CharField(max_length=150)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.attribute.label} | {self.label}"

    class Meta:
        db_table = "category_attribute_options"
        verbose_name = "Kategoriya atributi varianti"
        verbose_name_plural = "Kategoriya atributi variantlari"
        constraints = [
            models.UniqueConstraint(fields=["attribute", "value"], name="unique_attribute_option_value"),
        ]
        indexes = [
            models.Index(fields=["attribute", "is_active", "sort_order"], name="attr_option_active_sort_idx"),
        ]


class ListingAttributeValue(BaseModel):
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name="listing_values")
    option = models.ForeignKey(CategoryAttributeOption, on_delete=models.SET_NULL, null=True, blank=True, related_name="listing_values")
    value_text = models.CharField(max_length=255, blank=True, default="")
    value_int = models.BigIntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    value_bool = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.listing.title} | {self.attribute.label}"

    class Meta:
        db_table = "listing_attribute_values"
        verbose_name = "E'lon atribut qiymati"
        verbose_name_plural = "E'lon atribut qiymatlari"
        constraints = [
            models.UniqueConstraint(fields=["listing", "attribute"], name="unique_listing_attribute_value"),
        ]
        indexes = [
            models.Index(fields=["listing", "attribute"], name="listing_attr_value_idx"),
        ]


class Region(BaseModel):
    name = models.CharField(max_length=120, unique=True, db_index=True)
    slug = models.SlugField(unique=True,null=True,blank=True)
    type = models.CharField(max_length=20, choices=RegionTypeChoice.choices, default=RegionTypeChoice.CITY)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug

            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "regions"
        verbose_name = "Hudud"
        verbose_name_plural = "Hududlar"


class District(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(unique=True,blank=True,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.region.name} | {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug

            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "districts"
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        constraints = [
            models.UniqueConstraint(fields=["region", "slug"], name="unique_region_district_slug")
        ]


class Listing(BaseModel):
    title = models.CharField(max_length=150,verbose_name="Nom",db_index=True)
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=14, decimal_places=2, db_index=True)
    currency = models.CharField(max_length=30, choices=CurrencyChoice.choices, default=CurrencyChoice.UZS, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    listing_category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="category_listings")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_listings")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    condition = models.CharField(max_length=10, choices=ConditionChoice.choices, default=ConditionChoice.NEW)
    latitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=255, blank=True)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_negotiable = models.BooleanField(default=False)
    has_delivery = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=StatusChoice.choices, default=StatusChoice.ACTIVE ,db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("listing:detail", kwargs={"uuid": self.id})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "listings"
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        indexes = [
            models.Index(fields=["listing_category", "status"],name="listing_category_status_idx"),
            models.Index(fields=["listing_category", "price"],name="listing_category_price_idx"),
            models.Index(fields=["listing_category", "currency"],name="listing_category_currency_idx"),
            models.Index(fields=["region", "district", "status"],name="region_district_status_idx"),
            models.Index(fields=["created_at", "status"],name="created_at_status_idx"),
        ]


class ListingView(BaseModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_views", null=True, blank=True)
    session_key = models.CharField(max_length=64, blank=True,null=True)

    def __str__(self):
        return f"{self.listing.title} view"

    class Meta:
        db_table = "listing_views"
        verbose_name = "E'lon ko'rilishi"
        verbose_name_plural = "E'lon ko'rilishlari"
        indexes = [
            models.Index(fields=["listing", "created_at"], name="lview_listing_created_idx"),
            models.Index(fields=["user", "created_at"], name="lview_user_created_idx"),
            models.Index(fields=["session_key", "created_at"], name="lview_session_created_idx"),
        ]
        unique_together = ['listing','user']

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="listings/%Y/%m/%d/",default="")
    is_main = models.BooleanField(default=False,verbose_name="Rasm asosiymi")
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.listing.title}-ning rasmi"


class ListingContact(BaseModel):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="contact")
    phone_number = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=120)
    allow_chat = models.BooleanField(default=True)
    allow_call = models.BooleanField(default=False)
    allow_telegram = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.listing.title} contact"

    class Meta:
        db_table = "listing_contacts"
        verbose_name = "E'lon aloqa ma'lumoti"
        verbose_name_plural = "E'lon aloqa ma'lumotlari"


class ListingPromotion(BaseModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="promotions")
    promotion_type = models.CharField(max_length=20, choices=PromotionTypeChoice.choices)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.listing.title} | {self.promotion_type}"

    class Meta:
        db_table = "listing_promotions"
        verbose_name = "E'lon promo"
        verbose_name_plural = "E'lon promolari"


class ListingReport(BaseModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="listing_reports", null=True, blank=True)
    reason = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ReportStatusChoice.choices, default=ReportStatusChoice.NEW)

    def __str__(self):
        return f"{self.listing.title} | {self.reason}"

    class Meta:
        db_table = "listing_reports"
        verbose_name = "E'lon shikoyati"
        verbose_name_plural = "E'lon shikoyatlari"
