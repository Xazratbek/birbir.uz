from rest_framework import serializers
from accounts.serializers import UserSerializer
from categories.serializers import CategorySerializer
from .models import *

class RegionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name", "slug", "type", "is_active"]


class DistrictListSerializer(serializers.ModelSerializer):
    region = RegionListSerializer()

    class Meta:
        model = District
        fields = ["id", "name", "slug", "is_active", "region"]


class CategoryAttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAttributeOption
        fields = ["id", "value", "label", "sort_order", "is_active"]


class CategoryAttributeSerializer(serializers.ModelSerializer):
    options = CategoryAttributeOptionSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryAttribute
        fields = [
            "id",
            "key",
            "label",
            "value_type",
            "is_required",
            "is_filterable",
            "is_searchable",
            "unit",
            "sort_order",
            "is_active",
            "options",
        ]


class ListingAttributeValueSerializer(serializers.ModelSerializer):
    attribute = CategoryAttributeSerializer(read_only=True)
    option = CategoryAttributeOptionSerializer(read_only=True)
    display_value = serializers.SerializerMethodField()

    class Meta:
        model = ListingAttributeValue
        fields = [
            "id",
            "attribute",
            "option",
            "value_text",
            "value_int",
            "value_decimal",
            "value_bool",
            "display_value",
        ]

    def get_display_value(self, obj):
        if obj.option:
            return obj.option.label
        if obj.value_text not in ("", None):
            return obj.value_text
        if obj.value_int is not None:
            return obj.value_int
        if obj.value_decimal is not None:
            return obj.value_decimal
        if obj.value_bool is not None:
            return obj.value_bool
        return None


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "listing", "image", "is_main", "sort_order"]


class ListingContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingContact
        fields = ["id", "phone_number", "contact_name", "allow_chat", "allow_call", "allow_telegram"]


class ListingListSerializer(serializers.ModelSerializer):
    condition = serializers.CharField(source="get_condition_display", read_only=True)
    currency = serializers.CharField(source="get_currency_display", read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ["id", "title", "price", "condition", "currency", "images", "created_at"]


class ListingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing_category = CategorySerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    attribute_values = ListingAttributeValueSerializer(many=True, read_only=True)
    contact = ListingContactSerializer(read_only=True)
    condition = serializers.CharField(source="get_condition_display", read_only=True)
    currency = serializers.CharField(source="get_currency_display", read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)
    total_views = serializers.SerializerMethodField()
    region = RegionListSerializer(read_only=True)
    district = DistrictListSerializer(read_only=True)

    def get_total_views(self, obj):
        return obj.total_views

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "price",
            "currency",
            "listing_category",
            "user",
            "condition",
            "latitude",
            "longitude",
            "status",
            "total_views",
            "address",
            "landmark",
            "is_negotiable",
            "has_delivery",
            "published_at",
            "expires_at",
            "region",
            "district",
            "images",
            "attribute_values",
            "contact",
        ]


class ListingAttributeInputSerializer(serializers.Serializer):
    attribute_id = serializers.UUIDField()
    option_id = serializers.UUIDField(required=False, allow_null=True)
    value_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    value_int = serializers.IntegerField(required=False, allow_null=True)
    value_decimal = serializers.DecimalField(max_digits=18, decimal_places=6, required=False, allow_null=True)
    value_bool = serializers.BooleanField(required=False, allow_null=True)


class ListingCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.ChoiceField(choices=Listing._meta.get_field("currency").choices)
    category_id = serializers.UUIDField()
    latitude = serializers.DecimalField(max_digits=15, decimal_places=12)
    longitude = serializers.DecimalField(max_digits=15, decimal_places=12)
    address = serializers.CharField(max_length=255, allow_blank=True, required=False)
    landmark = serializers.CharField(max_length=255, allow_blank=True, required=False)
    contact_name = serializers.CharField(max_length=120, allow_blank=True, required=False)
    contact_phone = serializers.CharField(max_length=20, allow_blank=True, required=False)
    allow_chat = serializers.BooleanField(required=False, default=True)
    allow_call = serializers.BooleanField(required=False, default=False)
    allow_telegram = serializers.BooleanField(required=False, default=False)
    has_delivery = serializers.BooleanField(required=False, default=False)
    is_negotiable = serializers.BooleanField(required=False, default=False)
    condition = serializers.CharField(required=True)
    attributes = ListingAttributeInputSerializer(many=True, required=False, default=list)
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=True, use_url=False),
        min_length=1,
        max_length=10,
        write_only=True,
    )

    def validate_attributes(self, value):
        category_id = self.initial_data.get("category_id")
        if not category_id:
            return value

        category_attributes = CategoryAttribute.objects.filter(category_id=category_id, is_active=True).select_related("category")
        attribute_map = {str(attribute.id): attribute for attribute in category_attributes}

        seen_attribute_ids = set()
        for item in value:
            attribute_id = str(item.get("attribute_id"))
            if attribute_id in seen_attribute_ids:
                raise serializers.ValidationError("Bitta atribut bir martadan ko‘p yuborilmasligi kerak.")
            seen_attribute_ids.add(attribute_id)

            attribute = attribute_map.get(attribute_id)
            if attribute is None:
                raise serializers.ValidationError(f"Noma'lum atribut: {attribute_id}")

            provided_fields = [
                field_name
                for field_name in ["value_text", "value_int", "value_decimal", "value_bool", "option_id"]
                if item.get(field_name) not in (None, "", [])
            ]

            if attribute.value_type == "select":
                if item.get("option_id") is None:
                    raise serializers.ValidationError(f"{attribute.label} uchun option tanlanishi kerak.")
                if len(provided_fields) != 1:
                    raise serializers.ValidationError(f"{attribute.label} uchun faqat option yuborish kerak.")
                if not attribute.options.filter(id=item["option_id"], is_active=True).exists():
                    raise serializers.ValidationError(f"{attribute.label} uchun noto‘g‘ri option tanlangan.")
                continue

            expected_field_map = {
                "text": "value_text",
                "integer": "value_int",
                "decimal": "value_decimal",
                "boolean": "value_bool",
            }
            expected_field = expected_field_map.get(attribute.value_type)
            if expected_field is None:
                raise serializers.ValidationError(f"{attribute.label} atribut turi noto‘g‘ri sozlangan.")

            if item.get(expected_field) in (None, ""):
                raise serializers.ValidationError(f"{attribute.label} uchun qiymat kiritish kerak.")

            if len(provided_fields) != 1:
                raise serializers.ValidationError(f"{attribute.label} uchun faqat bitta qiymat yuborish kerak.")

        required_attribute_ids = set(
            str(attribute.id)
            for attribute in category_attributes
            if attribute.is_required
        )
        missing_required = required_attribute_ids - seen_attribute_ids
        if missing_required:
            missing_labels = list(
                category_attributes.filter(id__in=missing_required).values_list("label", flat=True)
            )
            raise serializers.ValidationError(
                {"attributes": f"Majburiy atributlar yetishmayapti: {', '.join(missing_labels)}"}
            )

        return value

    def validate(self, attrs):
        if not (attrs.get("allow_chat") or attrs.get("allow_call") or attrs.get("allow_telegram")):
            raise serializers.ValidationError("Kamida bitta aloqa usuli tanlanishi kerak.")
        return attrs


class ListingReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingReport
        fields = ['listing','reason','comment']

class ListingPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPromotion
        fields = ['listing','promotion_type','starts_at','ends_at','is_active']