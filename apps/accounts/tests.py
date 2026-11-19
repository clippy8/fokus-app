from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_framework.authtoken.models import Token

from .models import Profile


class RegisterViewTests(TestCase):
    def test_register_creates_user_profile_token_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password1": "a-very-strong-password-123",
                "password2": "a-very-strong-password-123",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(Token.objects.filter(user=user).exists())

        dashboard_response = self.client.get(reverse("dailydash:today"))
        self.assertEqual(dashboard_response.status_code, 302)
        self.assertNotIn("/accounts/login/", dashboard_response.url)

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser2",
                "password1": "a-very-strong-password-123",
                "password2": "does-not-match",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser2").exists())
