import random
import string
import uuid

import requests
from django.conf import settings


def generate_username():
    return f"user_{uuid.uuid4().hex[:10]}"


def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms(phone_number: str, message: str):
    provider = getattr(settings, "SMS_PROVIDER", "console")

    if provider == "textbelt":
        api_key = getattr(settings, "TEXTBELT_API_KEY", "textbelt")
        response = requests.post(
            "https://textbelt.com/text",
            data={"phone": phone_number, "message": message, "key": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise ValueError(data.get("error", "Textbelt SMS xatosi"))
        return data

    print(f"[SMS-CONSOLE] {phone_number}: {message}")
    return {"success": True, "provider": "console"}
