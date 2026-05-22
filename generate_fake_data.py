import os
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from accounts.models import SellerProfile, User
from categories.models import Category
from listings.models import District, Listing, ListingContact, Region


CATEGORY_TREE = {
    "Elektronika": {
        "Telefonlar va aloqa": [
            "Mobil telefonlar",
            "Aksessuarlar",
            "Aqlli soatlar",
            "SIM kartalar",
        ],
        "Kompyuterlar": [
            "Noutbuklar",
            "Kompyuter aksessuarlari",
        ],
        "Audio va video": [
            "Naushniklar",
            "Karnaylar",
        ],
    },
    "Avtomobillar": {
        "Yengil avtomobillar": [
            "Sedanlar",
            "Krossoverlar",
        ],
        "Ehtiyot qismlar": [
            "Dvigatel qismlari",
            "Susalma qismlar",
        ],
    },
    "Uy va bog'": {
        "Mebel": [
            "Divanlar",
            "Shkaflar",
        ],
        "Qurilish va remont": [
            "Asbob-uskunalar",
            "Qurilish materiallari",
        ],
    },
    "Kiyim va poyabzal": {
        "Ayollar kiyimi": [
            "Kurtkalar",
            "Ko'ylaklar",
        ],
        "Erkaklar kiyimi": [
            "Shimlar",
            "Koylaklar",
        ],
        "Bolalar kiyimi": [
            "Bolalar kiyimi",
            "Bolalar poyabzali",
        ],
    },
    "Bolalar uchun": {
        "O'yinchoqlar": [
            "Yumshoq o'yinchoqlar",
            "Transport o'yinchoqlari",
        ],
        "Bolalar buyumlari": [
            "Aravachalar",
            "Kreslolar",
        ],
    },
    "Go'zallik va salomatlik": {
        "Gigiena vositalari": [
            "Sovunlar",
            "Dezodorantlar",
        ],
        "Soch uchun mahsulotlar": [
            "Shampunlar",
            "Niqoblar",
        ],
    },
    "Xizmatlar": {
        "Ta'mirlash": [
            "Uy ta'miri",
            "Texnika ta'miri",
        ],
        "Yetkazib berish": [
            "Kuryer xizmati",
        ],
    },
}


REGION_DISTRICTS = {
    "Toshkent shahri": [
        "Shayxontohur",
        "Yunusobod",
        "Chilonzor",
        "Yakkasaroy",
        "Mirzo Ulug'bek",
        "Uchtepa",
    ],
    "Toshkent viloyati": [
        "Olmaliq",
        "Chirchiq",
        "Angren",
        "Bekobod",
        "Yangiyo'l",
    ],
    "Andijon viloyati": [
        "Andijon",
        "Asaka",
        "Shahrixon",
    ],
    "Farg'ona viloyati": [
        "Farg'ona",
        "Marg'ilon",
        "Qo'qon",
    ],
    "Namangan viloyati": [
        "Namangan",
        "Chust",
        "Uchqo'rg'on",
    ],
    "Samarqand viloyati": [
        "Samarqand",
        "Urgut",
        "Kattaqo'rg'on",
    ],
    "Buxoro viloyati": [
        "Buxoro",
        "G'ijduvon",
        "Kogon",
    ],
    "Xorazm viloyati": [
        "Urganch",
        "Xiva",
        "Hazorasp",
    ],
    "Qashqadaryo viloyati": [
        "Qarshi",
        "Shahrisabz",
        "Koson",
    ],
    "Surxondaryo viloyati": [
        "Termiz",
        "Denov",
        "Sho'rchi",
    ],
    "Sirdaryo viloyati": [
        "Guliston",
        "Yangiyer",
        "Sirdaryo",
    ],
    "Jizzax viloyati": [
        "Jizzax",
        "G'allaorol",
        "Do'stlik",
    ],
    "Navoiy viloyati": [
        "Navoiy",
        "Zarafshon",
        "Karmana",
    ],
    "Qoraqalpog'iston Respublikasi": [
        "Nukus",
        "Taxiatosh",
        "Xo'jayli",
    ],
}


DISTRICT_COORDS = {
    "Shayxontohur": (Decimal("41.3167"), Decimal("69.2550")),
    "Yunusobod": (Decimal("41.3640"), Decimal("69.2870")),
    "Chilonzor": (Decimal("41.2800"), Decimal("69.2000")),
    "Yakkasaroy": (Decimal("41.2760"), Decimal("69.2350")),
    "Mirzo Ulug'bek": (Decimal("41.3400"), Decimal("69.3300")),
    "Uchtepa": (Decimal("41.2650"), Decimal("69.1900")),
    "Olmaliq": (Decimal("40.8450"), Decimal("69.6000")),
    "Chirchiq": (Decimal("41.4700"), Decimal("69.5900")),
    "Angren": (Decimal("41.0160"), Decimal("70.1400")),
    "Bekobod": (Decimal("40.2200"), Decimal("69.2700")),
    "Yangiyo'l": (Decimal("41.1200"), Decimal("69.0500")),
    "Andijon": (Decimal("40.7800"), Decimal("72.3400")),
    "Asaka": (Decimal("40.6300"), Decimal("72.2400")),
    "Shahrixon": (Decimal("40.7100"), Decimal("72.0700")),
    "Farg'ona": (Decimal("40.3900"), Decimal("71.7800")),
    "Marg'ilon": (Decimal("40.4800"), Decimal("71.7200")),
    "Qo'qon": (Decimal("40.5300"), Decimal("70.9400")),
    "Namangan": (Decimal("41.0000"), Decimal("71.6700")),
    "Chust": (Decimal("41.0000"), Decimal("71.2400")),
    "Uchqo'rg'on": (Decimal("41.1100"), Decimal("72.0800")),
    "Samarqand": (Decimal("39.6500"), Decimal("66.9700")),
    "Urgut": (Decimal("39.4000"), Decimal("67.2500")),
    "Kattaqo'rg'on": (Decimal("39.9000"), Decimal("66.2600")),
    "Buxoro": (Decimal("39.7700"), Decimal("64.4200")),
    "G'ijduvon": (Decimal("40.1000"), Decimal("64.6800")),
    "Kogon": (Decimal("39.7300"), Decimal("64.5500")),
    "Urganch": (Decimal("41.5500"), Decimal("60.6300")),
    "Xiva": (Decimal("41.3800"), Decimal("60.3600")),
    "Hazorasp": (Decimal("41.3200"), Decimal("61.0700")),
    "Qarshi": (Decimal("38.8600"), Decimal("65.7900")),
    "Shahrisabz": (Decimal("39.0500"), Decimal("66.8300")),
    "Koson": (Decimal("38.9800"), Decimal("65.5800")),
    "Termiz": (Decimal("37.2300"), Decimal("67.2700")),
    "Denov": (Decimal("38.2700"), Decimal("67.9000")),
    "Sho'rchi": (Decimal("37.9900"), Decimal("67.7900")),
    "Guliston": (Decimal("40.4900"), Decimal("68.7900")),
    "Yangiyer": (Decimal("40.2800"), Decimal("68.8200")),
    "Sirdaryo": (Decimal("40.8200"), Decimal("68.6600")),
    "Jizzax": (Decimal("40.1100"), Decimal("67.8400")),
    "G'allaorol": (Decimal("40.0800"), Decimal("67.8300")),
    "Do'stlik": (Decimal("40.2200"), Decimal("68.0200")),
    "Navoiy": (Decimal("40.1000"), Decimal("65.3700")),
    "Zarafshon": (Decimal("41.5700"), Decimal("64.2100")),
    "Karmana": (Decimal("40.1400"), Decimal("65.3000")),
    "Nukus": (Decimal("42.4600"), Decimal("59.6100")),
    "Taxiatosh": (Decimal("42.3300"), Decimal("59.1800")),
    "Xo'jayli": (Decimal("42.4000"), Decimal("59.4600")),
}


SEED_USERS = [
    {"username": "seller_one", "phone_number": "+998901110001", "display_name": "Seller One"},
    {"username": "seller_two", "phone_number": "+998901110002", "display_name": "Seller Two"},
    {"username": "seller_three", "phone_number": "+998901110003", "display_name": "Seller Three"},
    {"username": "seller_four", "phone_number": "+998901110004", "display_name": "Seller Four"},
    {"username": "seller_five", "phone_number": "+998901110005", "display_name": "Seller Five"},
]


SEED_LISTINGS = [
    {
        "title": "iPhone 13 Pro 256GB",
        "description": "Ideal holat. Karobka bor. Narx kelishiladi.",
        "price": Decimal("8500000"),
        "currency": "uzs",
        "category_path": ["Elektronika", "Telefonlar va aloqa", "Mobil telefonlar"],
        "region": "Toshkent shahri",
        "district": "Shayxontohur",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": False,
    },
    {
        "title": "Samsung Galaxy A05 128/4",
        "description": "Yangi holatga yaqin. Toza ishlatilgan.",
        "price": Decimal("1800000"),
        "currency": "uzs",
        "category_path": ["Elektronika", "Telefonlar va aloqa", "Mobil telefonlar"],
        "region": "Toshkent shahri",
        "district": "Yunusobod",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": True,
    },
    {
        "title": "Anker Power Bank 20000mAh",
        "description": "Original power bank. Tez quvvatlaydi.",
        "price": Decimal("320000"),
        "currency": "uzs",
        "category_path": ["Elektronika", "Telefonlar va aloqa", "Aksessuarlar"],
        "region": "Toshkent viloyati",
        "district": "Angren",
        "condition": "new",
        "is_negotiable": False,
        "has_delivery": True,
    },
    {
        "title": "Lenovo ThinkPad E14",
        "description": "Ish uchun qulay noutbuk. SSD va 16GB RAM.",
        "price": Decimal("6200000"),
        "currency": "uzs",
        "category_path": ["Elektronika", "Kompyuterlar", "Noutbuklar"],
        "region": "Samarqand viloyati",
        "district": "Samarqand",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": False,
    },
    {
        "title": "3 qavatli shkaf",
        "description": "Uy uchun katta shkaf. Holati yaxshi.",
        "price": Decimal("1100000"),
        "currency": "uzs",
        "category_path": ["Uy va bog'", "Mebel", "Shkaflar"],
        "region": "Toshkent viloyati",
        "district": "Chirchiq",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": True,
    },
    {
        "title": "Dr. Sante Hyaluron Hair Deep Hydration shampuni",
        "description": "Sochni namlantiruvchi shampun. 500 ml.",
        "price": Decimal("45000"),
        "currency": "uzs",
        "category_path": ["Go'zallik va salomatlik", "Soch uchun mahsulotlar", "Shampunlar"],
        "region": "Toshkent viloyati",
        "district": "Olmaliq",
        "condition": "new",
        "is_negotiable": False,
        "has_delivery": False,
    },
    {
        "title": "Bolalar velosipedi",
        "description": "Bolalar uchun qulay va yengil velosiped.",
        "price": Decimal("550000"),
        "currency": "uzs",
        "category_path": ["Bolalar uchun", "Bolalar buyumlari", "Aravachalar"],
        "region": "Namangan viloyati",
        "district": "Namangan",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": False,
    },
    {
        "title": "Chevrolet Cobalt 2020",
        "description": "Yangi avtosalon holatiga yaqin. Toza mashina.",
        "price": Decimal("115000000"),
        "currency": "uzs",
        "category_path": ["Avtomobillar", "Yengil avtomobillar", "Sedanlar"],
        "region": "Andijon viloyati",
        "district": "Asaka",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": False,
    },
    {
        "title": "Bosch matkap",
        "description": "Uy va remont uchun kuchli matkap.",
        "price": Decimal("780000"),
        "currency": "uzs",
        "category_path": ["Uy va bog'", "Qurilish va remont", "Asbob-uskunalar"],
        "region": "Buxoro viloyati",
        "district": "Buxoro",
        "condition": "new",
        "is_negotiable": False,
        "has_delivery": True,
    },
    {
        "title": "Ayollar kurtkasi",
        "description": "Kuzgi ayollar kurtkasi, holati zo'r.",
        "price": Decimal("260000"),
        "currency": "uzs",
        "category_path": ["Kiyim va poyabzal", "Ayollar kiyimi", "Kurtkalar"],
        "region": "Xorazm viloyati",
        "district": "Urganch",
        "condition": "used",
        "is_negotiable": True,
        "has_delivery": False,
    },
    {
        "title": "Uy ta'miri xizmati",
        "description": "Ichki ta'mir, bo'yoq, santexnika ishlari.",
        "price": Decimal("1500000"),
        "currency": "uzs",
        "category_path": ["Xizmatlar", "Ta'mirlash", "Uy ta'miri"],
        "region": "Qashqadaryo viloyati",
        "district": "Qarshi",
        "condition": "new",
        "is_negotiable": True,
        "has_delivery": False,
    },
]


def ensure_category(path):
    parent = None
    for name in path:
        category, _ = Category.objects.get_or_create(name=name, parent=parent)
        parent = category
    return parent


def seed_categories():
    leaf_categories = {}
    for top_name, children in CATEGORY_TREE.items():
        top_category, _ = Category.objects.get_or_create(name=top_name, parent=None)
        for child_name, leaf_names in children.items():
            child_category, _ = Category.objects.get_or_create(name=child_name, parent=top_category)
            for leaf_name in leaf_names:
                leaf_category, _ = Category.objects.get_or_create(name=leaf_name, parent=child_category)
                leaf_categories[tuple([top_name, child_name, leaf_name])] = leaf_category
    return leaf_categories


def seed_regions_and_districts():
    region_map = {}
    district_map = {}
    for region_name, district_names in REGION_DISTRICTS.items():
        region_type = "city" if region_name == "Toshkent shahri" else "region"
        region, _ = Region.objects.get_or_create(
            name=region_name,
            defaults={"type": region_type},
        )
        region_map[region_name] = region

        for district_name in district_names:
            district, _ = District.objects.get_or_create(
                region=region,
                name=district_name,
            )
            district_map[district_name] = district

    return region_map, district_map


def seed_users():
    users = {}
    for item in SEED_USERS:
        user, created = User.objects.get_or_create(
            username=item["username"],
            defaults={
                "phone_number": item["phone_number"],
                "auth_type": "phone",
                "is_phone_verified": True,
                "is_verified": True,
            },
        )
        if created:
            user.set_password("12345678")
            user.save(update_fields=["password"])
        else:
            changed = False
            if user.phone_number != item["phone_number"]:
                user.phone_number = item["phone_number"]
                changed = True
            if not user.auth_type:
                user.auth_type = "phone"
                changed = True
            if not user.is_phone_verified:
                user.is_phone_verified = True
                changed = True
            if not user.is_verified:
                user.is_verified = True
                changed = True
            if changed:
                user.save()

        SellerProfile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": item["display_name"],
                "is_store": False,
                "telegram_username": "",
                "phone_visible": True,
            },
        )
        users[item["username"]] = user

    return users


def seed_listings(users, region_map, district_map, leaf_categories):
    seller_cycle = list(users.values())
    created = 0

    for index, item in enumerate(SEED_LISTINGS):
        category = leaf_categories[tuple(item["category_path"])]
        region = region_map[item["region"]]
        district = district_map[item["district"]]
        lat, lon = DISTRICT_COORDS.get(item["district"], (None, None))
        user = seller_cycle[index % len(seller_cycle)]

        listing, was_created = Listing.objects.get_or_create(
            title=item["title"],
            user=user,
            defaults={
                "description": item["description"],
                "price": item["price"],
                "currency": item["currency"],
                "listing_category": category,
                "region": region,
                "district": district,
                "condition": item["condition"],
                "latitude": lat,
                "longitude": lon,
                "address": f"{item['district']}, {item['region']}",
                "landmark": item["district"],
                "contact_name": user.username,
                "contact_phone": user.phone_number or "",
                "is_negotiable": item["is_negotiable"],
                "has_delivery": item["has_delivery"],
                "status": "active",
            },
        )

        if not was_created:
            listing.description = item["description"]
            listing.price = item["price"]
            listing.currency = item["currency"]
            listing.listing_category = category
            listing.region = region
            listing.district = district
            listing.condition = item["condition"]
            listing.latitude = lat
            listing.longitude = lon
            listing.address = f"{item['district']}, {item['region']}"
            listing.landmark = item["district"]
            listing.contact_name = user.username
            listing.contact_phone = user.phone_number or ""
            listing.is_negotiable = item["is_negotiable"]
            listing.has_delivery = item["has_delivery"]
            listing.status = "active"
            listing.save()

        ListingContact.objects.update_or_create(
            listing=listing,
            defaults={
                "phone_number": user.phone_number or "",
                "contact_name": user.username,
                "allow_chat": True,
                "allow_call": False,
                "allow_telegram": True,
            },
        )
        created += int(was_created)

    return created


def main():
    leaf_categories = seed_categories()
    region_map, district_map = seed_regions_and_districts()
    users = seed_users()
    listings_created = seed_listings(users, region_map, district_map, leaf_categories)

    print(f"Seed done. Users: {len(users)}, regions: {len(region_map)}, districts: {len(district_map)}, new listings: {listings_created}")


if __name__ == "__main__":
    main()
