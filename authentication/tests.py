from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from accounts.models import User


class StartSignupViewTests(APITestCase):
    @patch("authentication.views.send_sms", return_value={"request_id": "req_test_1"})
    def test_phone_signup_does_not_store_empty_email(self):
        url = "/api/auth/signup/start/"

        first_response = self.client.post(url, {"phone_number": "+998901112233"}, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        first_user = User.objects.get(phone_number="+998901112233")
        self.assertIsNone(first_user.email)

        second_response = self.client.post(url, {"phone_number": "+998901112244"}, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        second_user = User.objects.get(phone_number="+998901112244")
        self.assertIsNone(second_user.email)
