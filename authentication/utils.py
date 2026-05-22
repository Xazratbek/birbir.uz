import random
import string
import uuid

def generate_username():
    return f"user_{uuid.uuid4().hex[:10]}"

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_otp():
    return str(random.randint(100000, 999999))