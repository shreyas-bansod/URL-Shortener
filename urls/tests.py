from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse

from .models import URL, ClickEvent
from .base62 import encode


class URLShortenerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_base62_encoding(self):
        self.assertEqual(encode(100), "1c")
        self.assertEqual(encode(1000), "G8")

    def test_create_url(self):
        response = self.client.post(
            "/api/urls",
            {
                "original_url": "https://www.google.com"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            URL.objects.filter(
                original_url="https://www.google.com"
            ).exists()
        )

    def test_invalid_url(self):
        response = self.client.post(
            "/api/urls",
            {
                "original_url": "hello"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_custom_alias(self):
        response = self.client.post(
            "/api/urls",
            {
                "original_url": "https://www.google.com",
                "custom_alias": "google"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            URL.objects.filter(
                custom_alias="google"
            ).exists()
        )

    def test_redirect_records_click(self):
        url = URL.objects.create(
            user=self.user,
            original_url="https://www.google.com",
            short_code="test1"
        )

        response = self.client.get("/test1")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ClickEvent.objects.filter(url=url).count(),
            1
        )