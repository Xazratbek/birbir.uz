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


def send_sms(phone_number: str):
    header = {
        "Authorization":"Bearer AAGnJAAA7qUMTqvgYu23eROzo_5tGZq_dt-YfNLtDTD9Tg",
        "Content-Type":"application/json"
              }
    data = {
        "phone_number": f"{phone_number}",
        "request_id": "166917350520803",
        "code_length": 6,
        "ttl": 300
        }
    url = "https://gatewayapi.telegram.org/sendVerificationMessage"
    res = requests.post(url=url,data=data,headers=header)
    return res.json()
