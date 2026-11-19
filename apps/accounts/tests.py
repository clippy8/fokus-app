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
        self.assertEqual(response.url, reverse("accounts:onboarding-profile"))
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


class OnboardingProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:onboarding-profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_fills_in_height_and_weight(self):
        response = self.client.post(
            reverse("accounts:onboarding-profile"),
            {"groesse_cm": "180", "gewicht_kg": "75.5"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dailydash:today"))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.groesse_cm, 180)
        self.assertEqual(str(self.user.profile.gewicht_kg), "75.50")

    def test_can_be_skipped_without_data(self):
        response = self.client.post(reverse("accounts:onboarding-profile"), {"skip": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dailydash:today"))
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.groesse_cm)

    def test_fields_are_optional(self):
        response = self.client.post(reverse("accounts:onboarding-profile"), {})
        self.assertEqual(response.status_code, 302)
