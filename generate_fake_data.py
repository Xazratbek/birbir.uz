"""
Django loyihasi uchun realga yaqin fake ma'lumotlar generatori.

- Modellar orasidagi bog'liqliklar saqlanadi.
- Image/file maydonlar bo'sh qoldiriladi.
- Ko'p hajmda data yaratish uchun parametrlar bor.

Ishlatish:
    python generate_fake_data.py
    python generate_fake_data.py --users 300 --listings 2500 --reset
"""

from __future__ import annotations

import argparse
import os
import random
from datetime import timedelta
from decimal import Decimal

import django
from django.db import connection, transaction
from django.utils import timezone
from django.utils.text import slugify
from django.utils.crypto import get_random_string


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import AuthType, SellerFollow, SellerProfile, User
from authentication.models import OTPCode, Purpose, RegistrationSession, Step
from categories.models import Category
from chat.models import ChatRoom, Message
from favorites.models import Favorite
from listings.models import (
    AttributeValueTypeChoice,
    CategoryAttribute,
    CategoryAttributeOption,
    ConditionChoice,
    CurrencyChoice,
    District,
    Listing,
    ListingAttributeValue,
    ListingContact,
    ListingPromotion,
    ListingReport,
    ListingView,
    PromotionTypeChoice,
    Region,
    RegionTypeChoice,
    ReportStatusChoice,
    StatusChoice,
)


REGION_DISTRICTS = {
    "Toshkent shahri": ["Yunusobod", "Chilonzor", "Mirzo Ulug'bek", "Sergeli", "Yakkasaroy"],
    "Toshkent viloyati": ["Qibray", "Yangiyo'l", "Chirchiq", "Angren", "Olmaliq"],
    "Samarqand": ["Samarqand shahar", "Urgut", "Jomboy", "Pastdarg'om", "Bulung'ur"],
    "Farg'ona": ["Farg'ona shahar", "Qo'qon", "Marg'ilon", "Quva", "Rishton"],
    "Namangan": ["Namangan shahar", "Chust", "Kosonsoy", "Pop", "To'raqo'rg'on"],
}

CATEGORY_TREE = {
    "Transport": ["Yengil avtomobillar", "Moto", "Ehtiyot qismlar"],
    "Ko'chmas mulk": ["Kvartira", "Hovli", "Ofis va noturar joy"],
    "Elektronika": ["Telefon", "Noutbuk", "Maishiy texnika"],
    "Ish va xizmatlar": ["Vakansiyalar", "Qurilish xizmatlari", "Ta'lim"],
    "Bolalar dunyosi": ["Kiyim-kechak", "O'yinchoqlar", "Bolalar aravachasi"],
}

ATTRIBUTE_SCHEMAS = {
    "Yengil avtomobillar": [
        ("brand", "Brend", AttributeValueTypeChoice.SELECT, True, ["Chevrolet", "Kia", "Toyota", "Hyundai", "BYD"]),
        ("year", "Yili", AttributeValueTypeChoice.INTEGER, True, None),
        ("mileage", "Yurgani (km)", AttributeValueTypeChoice.INTEGER, True, None),
        ("transmission", "Uzatma", AttributeValueTypeChoice.SELECT, True, ["manual", "automatic"]),
    ],
    "Telefon": [
        ("brand", "Brend", AttributeValueTypeChoice.SELECT, True, ["Apple", "Samsung", "Xiaomi", "Honor"]),
        ("storage", "Xotira", AttributeValueTypeChoice.SELECT, True, ["64gb", "128gb", "256gb", "512gb"]),
        ("battery", "Batareya holati", AttributeValueTypeChoice.INTEGER, False, None),
    ],
    "Kvartira": [
        ("rooms", "Xonalar soni", AttributeValueTypeChoice.INTEGER, True, None),
        ("area", "Maydon (m2)", AttributeValueTypeChoice.DECIMAL, True, None),
        ("floor", "Qavat", AttributeValueTypeChoice.INTEGER, False, None),
        ("furnished", "Jihozlangan", AttributeValueTypeChoice.BOOLEAN, False, None),
    ],
}

FIRST_NAMES = ["Aziz", "Jasur", "Sardor", "Oybek", "Diyor", "Madina", "Dilnoza", "Zarina", "Sevara", "Malika"]
LAST_NAMES = ["Karimov", "Rasulov", "Tursunov", "Aliyev", "Nazarov", "Yuldasheva", "Mamatova", "Sattorov"]

WORDS = [
    "toza", "tejamkor", "yangi", "ishonchli", "zudlik", "ideal", "kelishiladi", "egasi", "sifatli", "qulay"
]


def money_for_category(cat_name: str) -> tuple[Decimal, Decimal, str]:
    name = cat_name.lower()
    if "avto" in name or "moto" in name:
        return Decimal("3000"), Decimal("50000"), CurrencyChoice.USD
    if "kvartira" in name or "hovli" in name or "ofis" in name:
        return Decimal("15000"), Decimal("250000"), CurrencyChoice.USD
    if "telefon" in name or "noutbuk" in name or "elektronika" in name:
        return Decimal("150"), Decimal("4000"), CurrencyChoice.USD
    return Decimal("100000"), Decimal("12000000"), CurrencyChoice.UZS


def random_sentence(n: int = 10) -> str:
    return " ".join(random.choice(WORDS) for _ in range(n)).capitalize()


def make_username(first: str, last: str, idx: int) -> str:
    return f"{slugify(first)}_{slugify(last)}_{idx}"


def unique_username(first: str, last: str, idx: int) -> str:
    base = make_username(first, last, idx)
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}_{counter}"
        counter += 1
    return username




def safe_listing_title(category_name: str, index: int) -> str:
    base = f"{category_name} {random_sentence(2)}"
    suffix = f" #{index + 1}"
    max_len = 45
    trimmed = base[: max_len - len(suffix)].rstrip()
    if not trimmed:
        trimmed = get_random_string(8)
    return f"{trimmed}{suffix}"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Realga yaqin fake data generator")
    p.add_argument("--users", type=int, default=180)
    p.add_argument("--listings", type=int, default=1600)
    p.add_argument("--views-per-listing", type=int, default=9)
    p.add_argument("--messages-per-room", type=int, default=8)
    p.add_argument("--reset", action="store_true", help="Mavjud datani tozalab keyin yaratadi")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()




def get_existing_tables() -> set[str]:
    return set(connection.introspection.table_names())


def has_table(tables: set[str], table_name: str) -> bool:
    return table_name in tables


def build_feature_flags(tables: set[str]) -> dict[str, bool]:
    return {
        "category_attributes": has_table(tables, "category_attributes"),
        "category_attribute_options": has_table(tables, "category_attribute_options"),
        "listing_attribute_values": has_table(tables, "listing_attribute_values"),
        "listing_contacts": has_table(tables, "listing_contacts"),
        "listing_promotions": has_table(tables, "listing_promotions"),
        "listing_reports": has_table(tables, "listing_reports"),
        "listing_views": has_table(tables, "listing_views"),
        "favorites": has_table(tables, "favorites"),
        "chatrooms": has_table(tables, "chatrooms"),
        "messages": has_table(tables, "messages"),
        "seller_follows": has_table(tables, "seller_follows"),
    }

def clear_data(features: dict[str, bool]) -> None:
    if features["messages"]:
        Message.objects.all().delete()
    if features["chatrooms"]:
        ChatRoom.objects.all().delete()
    if features["favorites"]:
        Favorite.objects.all().delete()
    if features["listing_views"]:
        ListingView.objects.all().delete()
    if features["listing_promotions"]:
        ListingPromotion.objects.all().delete()
    if features["listing_reports"]:
        ListingReport.objects.all().delete()
    if features["listing_contacts"]:
        ListingContact.objects.all().delete()
    if features["listing_attribute_values"]:
        ListingAttributeValue.objects.all().delete()
    Listing.objects.all().delete()
    if features["category_attribute_options"]:
        CategoryAttributeOption.objects.all().delete()
    if features["category_attributes"]:
        CategoryAttribute.objects.all().delete()
    District.objects.all().delete()
    Region.objects.all().delete()
    Category.objects.all().delete()
    if features["seller_follows"]:
        SellerFollow.objects.all().delete()
    SellerProfile.objects.all().delete()
    RegistrationSession.objects.all().delete()
    OTPCode.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()


def create_users(total: int) -> list[User]:
    users: list[User] = []
    for i in range(total):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        username = unique_username(first, last, i + User.objects.count())

        auth_type = random.choice([AuthType.PHONE, AuthType.EMAIL])
        email = f"{username}@mail.uz" if auth_type == AuthType.EMAIL else None
        phone = f"+9989{random.randint(0,9)}{random.randint(1000000, 9999999)}" if auth_type == AuthType.PHONE else None

        user = User.objects.create_user(
            username=username,
            first_name=first,
            last_name=last,
            email=email,
            password="Test12345!",
            phone_number=phone,
            auth_type=auth_type,
            is_email_verified=bool(email),
            is_phone_verified=bool(phone),
            is_verified=True,
            bio=random_sentence(12),
            avatar=None,
        )
        users.append(user)

        SellerProfile.objects.create(
            user=user,
            display_name=f"{first} {last}",
            is_store=random.random() < 0.2,
            telegram_username=f"{slugify(first)}_{random.randint(100,999)}",
            phone_visible=random.random() < 0.85,
            reply_time_minutes=random.choice([5, 10, 15, 30, 60]),
        )
        RegistrationSession.objects.create(
            user=user,
            current_step=Step.COMPLETED,
            is_completed=True,
        )

        for _ in range(random.randint(1, 2)):
            expires_at = timezone.now() + timedelta(minutes=random.randint(2, 10))
            OTPCode.objects.create(
                email=email,
                phone_number=phone,
                code=f"{random.randint(0, 999999):06d}",
                purpose=random.choice([Purpose.LOGIN, Purpose.REGISTER]),
                is_used=random.random() < 0.7,
                expires_at=expires_at,
            )
    return users


def create_regions_and_categories(features: dict[str, bool]):
    regions = []
    for region_name, districts in REGION_DISTRICTS.items():
        r, _ = Region.objects.get_or_create(
            name=region_name,
            defaults={"type": random.choice([RegionTypeChoice.CITY, RegionTypeChoice.REGION])},
        )
        regions.append(r)
        for d in districts:
            District.objects.get_or_create(region=r, name=d, defaults={"is_active": True})

    leaf_categories: list[Category] = []
    for parent_name, children in CATEGORY_TREE.items():
        parent, _ = Category.objects.get_or_create(name=parent_name, parent=None, defaults={"icon": None})
        for child_name in children:
            child, _ = Category.objects.get_or_create(name=child_name, parent=parent, defaults={"icon": None})
            leaf_categories.append(child)

    category_attributes = {}
    if features["category_attributes"]:
        for leaf in leaf_categories:
            schemas = ATTRIBUTE_SCHEMAS.get(leaf.name, [])
            attrs = []
            for idx, (key, label, vtype, required, options) in enumerate(schemas):
                attr, _ = CategoryAttribute.objects.get_or_create(
                    category=leaf,
                    key=key,
                    defaults={
                        "label": label,
                        "value_type": vtype,
                        "is_required": required,
                        "is_filterable": True,
                        "is_searchable": True,
                        "sort_order": idx,
                    },
                )
                if options and features["category_attribute_options"]:
                    for sidx, opt in enumerate(options):
                        CategoryAttributeOption.objects.get_or_create(
                            attribute=attr,
                            value=slugify(opt),
                            defaults={"label": str(opt), "sort_order": sidx},
                        )
                attrs.append(attr)
            category_attributes[leaf.id] = attrs

    return regions, leaf_categories, category_attributes


def add_attribute_values(listing: Listing, attrs: list[CategoryAttribute], features: dict[str, bool]) -> None:
    if not features["listing_attribute_values"]:
        return
    for attr in attrs:
        payload = dict(listing=listing, attribute=attr)
        if attr.value_type == AttributeValueTypeChoice.SELECT:
            option = attr.options.order_by("sort_order").first()
            if option:
                payload["option"] = random.choice(list(attr.options.all()))
        elif attr.value_type == AttributeValueTypeChoice.INTEGER:
            payload["value_int"] = random.randint(1, 450)
        elif attr.value_type == AttributeValueTypeChoice.DECIMAL:
            payload["value_decimal"] = Decimal(str(round(random.uniform(20, 260), 2)))
        elif attr.value_type == AttributeValueTypeChoice.BOOLEAN:
            payload["value_bool"] = random.random() < 0.5
        else:
            payload["value_text"] = random_sentence(3)
        ListingAttributeValue.objects.create(**payload)


def create_listings(users: list[User], regions: list[Region], categories: list[Category], attrs_map: dict, total: int, features: dict[str, bool]):
    listings: list[Listing] = []
    for i in range(total):
        cat = random.choice(categories)
        region = random.choice(regions)
        district = random.choice(list(region.districts.all()))
        low, high, currency = money_for_category(cat.name)
        seller = random.choice(users)

        title = safe_listing_title(cat.name, i)
        price_val = Decimal(str(round(random.uniform(float(low), float(high)), 2)))
        created_shift = random.randint(0, 90)
        published_at = timezone.now() - timedelta(days=created_shift, hours=random.randint(0, 23))
        expires_at = published_at + timedelta(days=random.randint(20, 70))

        listing = Listing.objects.create(
            title=title,
            description=f"{random_sentence(18)}. {random_sentence(16)}.",
            price=price_val,
            currency=currency,
            listing_category=cat,
            user=seller,
            region=region,
            district=district,
            condition=random.choice([ConditionChoice.NEW, ConditionChoice.USED]),
            latitude=Decimal(str(round(41.0 + random.uniform(-0.4, 0.4), 12))),
            longitude=Decimal(str(round(69.0 + random.uniform(-0.6, 0.6), 12))),
            address=f"{district.name}, {random.randint(1,120)}-uy",
            landmark=f"{random.choice(['Bozor', 'Bekat', 'Metro', 'Park'])} yaqinida",
            contact_name=seller.get_full_name() or seller.username,
            contact_phone=seller.phone_number or f"+99890{random.randint(1000000, 9999999)}",
            is_negotiable=random.random() < 0.6,
            has_delivery=random.random() < 0.4,
            status=random.choice([StatusChoice.ACTIVE, StatusChoice.ACTIVE, StatusChoice.SOLD, StatusChoice.ARCHIVED]),
            published_at=published_at,
            expires_at=expires_at,
        )
        listings.append(listing)

        if features["listing_contacts"]:
            ListingContact.objects.create(
            listing=listing,
            phone_number=listing.contact_phone,
            contact_name=listing.contact_name,
            allow_chat=True,
            allow_call=random.random() < 0.7,
            allow_telegram=random.random() < 0.45,
        )

        if features["listing_promotions"] and random.random() < 0.32:
            start = published_at + timedelta(days=random.randint(0, 5))
            end = start + timedelta(days=random.randint(3, 14))
            ListingPromotion.objects.create(
                listing=listing,
                promotion_type=random.choice(PromotionTypeChoice.values),
                starts_at=start,
                ends_at=end,
                is_active=end >= timezone.now(),
            )

        if features["listing_reports"]:
            for _ in range(random.randint(0, 2)):
                reporter = random.choice(users)
                if reporter.id == seller.id:
                    continue
                ListingReport.objects.create(
                listing=listing,
                reporter=reporter,
                reason=random.choice(["Noto'g'ri narx", "Spam", "Aldov", "Takror e'lon"]),
                comment=random_sentence(8),
                status=random.choice(ReportStatusChoice.values),
            )

        add_attribute_values(listing, attrs_map.get(cat.id, []), features)

    return listings


def create_relations(users: list[User], listings: list[Listing], views_per_listing: int, messages_per_room: int, features: dict[str, bool]):
    for listing in listings:
        if features["listing_views"]:
            viewer_pool = random.sample(users, k=min(len(users), random.randint(3, views_per_listing + 3)))
            for viewer in viewer_pool:
                if viewer.id == listing.user_id:
                    continue
                ListingView.objects.get_or_create(listing=listing, user=viewer)

        if features["favorites"]:
            fav_pool = random.sample(users, k=min(len(users), random.randint(2, 8)))
            for u in fav_pool:
                if u.id != listing.user_id:
                    Favorite.objects.get_or_create(user=u, favorite_listing=listing)

        if features["chatrooms"] and features["messages"] and len(users) > 2:
            buyers = random.sample(users, k=min(len(users), random.randint(1, 5)))
            for buyer in buyers:
                if buyer.id == listing.user_id:
                    continue
                room, _ = ChatRoom.objects.get_or_create(chat_listing=listing, buyer=buyer, seller=listing.user)
                sender = buyer
                for _ in range(random.randint(2, messages_per_room)):
                    Message.objects.create(
                        room=room,
                        sender=sender,
                        text=random_sentence(random.randint(6, 16)),
                        is_read=random.random() < 0.65,
                    )
                    sender = listing.user if sender.id == buyer.id else buyer

    sellers = [u for u in users if hasattr(u, "seller_profile")]
    if features["seller_follows"]:
        for follower in users:
            follow_count = random.randint(0, min(8, len(sellers)))
            for seller in random.sample(sellers, k=follow_count):
                if follower.id != seller.id:
                    SellerFollow.objects.get_or_create(follower=follower, seller=seller)

    for seller in sellers:
        active_count = Listing.objects.filter(user=seller, status=StatusChoice.ACTIVE).count()
        SellerProfile.objects.filter(user=seller).update(active_listing_count=active_count)


def main():
    args = parse_args()
    random.seed(args.seed)

    tables = get_existing_tables()
    features = build_feature_flags(tables)

    with transaction.atomic():
        if args.reset:
            clear_data(features)

        users = create_users(args.users)
        regions, categories, attrs_map = create_regions_and_categories(features)
        listings = create_listings(users, regions, categories, attrs_map, args.listings, features)
        create_relations(users, listings, args.views_per_listing, args.messages_per_room, features)

    print("✅ Fake data yaratildi:")
    print(f"   Users: {User.objects.count()}")
    print(f"   SellerProfiles: {SellerProfile.objects.count()}")
    print(f"   Categories: {Category.objects.count()}")
    print(f"   Listings: {Listing.objects.count()}")
    print(f"   ListingAttributeValues: {ListingAttributeValue.objects.count()}")
    print(f"   Views: {ListingView.objects.count()}")
    print(f"   Favorites: {Favorite.objects.count()}")
    print(f"   ChatRooms: {ChatRoom.objects.count()}")
    print(f"   Messages: {Message.objects.count()}")


if __name__ == "__main__":
    main()
