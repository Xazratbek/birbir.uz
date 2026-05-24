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


def _get_gateway_headers():
    return {
        "Authorization": f"Bearer {settings.TELEGRAM_GATEWAY_TOKEN}",
        "Content-Type": "application/json",
    }


def send_sms(phone_number: str):
    data = {
        "phone_number": f"{phone_number}",
        "code_length": 6,
        "ttl": 300,
    }
    url = "https://gatewayapi.telegram.org/sendVerificationMessage"
    res = requests.post(url=url, json=data, headers=_get_gateway_headers(), timeout=10)
    res.raise_for_status()
    return res.json()


def verify_sms_code(request_id: str, code: str):
    data = {
        "request_id": request_id,
        "code": code,
    }
    url = "https://gatewayapi.telegram.org/checkVerificationStatus"
    res = requests.post(url=url, json=data, headers=_get_gateway_headers(), timeout=10)
    res.raise_for_status()
    payload = res.json()
    status_data = payload.get("verification_status") or {}
    return status_data.get("status") == "code_valid"
