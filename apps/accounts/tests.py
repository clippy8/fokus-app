from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.authtoken.models import Token

from apps.goals.models import Jahresziel, Meilenstein

from .models import Profile


def goal_formset_data(count=3):
    today = timezone.localdate()
    data = {
        "goal-TOTAL_FORMS": str(count),
        "goal-INITIAL_FORMS": "0",
        "goal-MIN_NUM_FORMS": "3",
        "goal-MAX_NUM_FORMS": "3",
    }
    for i in range(count):
        data.update(
            {
                f"goal-{i}-title": f"Ziel {i}",
                f"goal-{i}-description": "Konkrete Beschreibung.",
                f"goal-{i}-start_date": today.isoformat(),
                f"goal-{i}-end_date": (today + timedelta(days=300)).isoformat(),
                f"goal-{i}-start_value": "0",
                f"goal-{i}-target_value": "100",
            }
        )
    return data


def meilenstein_formset_data(prefix, count=3):
    today = timezone.localdate()
    data = {
        f"{prefix}-TOTAL_FORMS": str(count),
        f"{prefix}-INITIAL_FORMS": "0",
        f"{prefix}-MIN_NUM_FORMS": "3",
        f"{prefix}-MAX_NUM_FORMS": "3",
    }
    for i in range(count):
        data.update(
            {
                f"{prefix}-{i}-title": f"Meilenstein {i}",
                f"{prefix}-{i}-description": "Konkrete Beschreibung.",
                f"{prefix}-{i}-deadline": (today + timedelta(days=100)).isoformat(),
                f"{prefix}-{i}-start_value": "0",
                f"{prefix}-{i}-target_value": "10",
            }
        )
    return data


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

    def test_fills_in_height_weight_and_calorie_goal(self):
        response = self.client.post(
            reverse("accounts:onboarding-profile"),
            {"groesse_cm": "180", "gewicht_kg": "75.5", "kalorienziel_kcal": "2400"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:onboarding-goals"))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.groesse_cm, 180)
        self.assertEqual(str(self.user.profile.gewicht_kg), "75.50")
        self.assertEqual(self.user.profile.kalorienziel_kcal, 2400)

    def test_can_be_skipped_without_data(self):
        response = self.client.post(reverse("accounts:onboarding-profile"), {"skip": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:onboarding-goals"))
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.groesse_cm)

    def test_fields_are_optional(self):
        response = self.client.post(reverse("accounts:onboarding-profile"), {})
        self.assertEqual(response.status_code, 302)


class OnboardingGoalsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:onboarding-goals"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_creates_exactly_three_goals_and_redirects_to_next_step(self):
        response = self.client.post(reverse("accounts:onboarding-goals"), goal_formset_data(3))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:onboarding-meilensteine"))
        goals = Jahresziel.objects.filter(user=self.user).order_by("title")
        self.assertEqual(goals.count(), 3)
        for goal in goals:
            self.assertEqual(goal.status, Jahresziel.ON_TRACK)
            self.assertEqual(goal.current_value, goal.start_value)

    def test_rejects_fewer_than_three_goals(self):
        data = goal_formset_data(3)
        # Blank out the third goal's required fields to simulate an incomplete submission.
        for key in list(data):
            if key.startswith("goal-2-"):
                data[key] = ""
        response = self.client.post(reverse("accounts:onboarding-goals"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Jahresziel.objects.filter(user=self.user).count(), 0)

    def test_already_having_three_goals_skips_to_next_step(self):
        today = timezone.localdate()
        for i in range(3):
            Jahresziel.objects.create(
                user=self.user,
                title=f"Bestehendes Ziel {i}",
                description="x",
                start_date=today,
                end_date=today + timedelta(days=300),
            )
        response = self.client.get(reverse("accounts:onboarding-goals"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:onboarding-meilensteine"))


class OnboardingMeilensteineViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)
        today = timezone.localdate()
        self.ziele = [
            Jahresziel.objects.create(
                user=self.user,
                title=f"Ziel {i}",
                description="x",
                start_date=today,
                end_date=today + timedelta(days=300),
            )
            for i in range(3)
        ]

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:onboarding-meilensteine"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_redirects_to_dashboard_if_no_goals(self):
        self.ziele[0].delete()
        self.ziele[1].delete()
        self.ziele[2].delete()
        response = self.client.get(reverse("accounts:onboarding-meilensteine"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dailydash:today"))

    def test_creates_three_milestones_per_goal(self):
        data = {}
        for ziel in self.ziele:
            data.update(meilenstein_formset_data(f"ziel{ziel.id}"))
        response = self.client.post(reverse("accounts:onboarding-meilensteine"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dailydash:today"))
        for ziel in self.ziele:
            meilensteine = Meilenstein.objects.filter(jahresziel=ziel)
            self.assertEqual(meilensteine.count(), 3)
            for m in meilensteine:
                self.assertEqual(m.status, Meilenstein.NOT_STARTED)
                self.assertEqual(m.current_value, m.start_value)

    def test_rejects_fewer_than_three_milestones_for_one_goal(self):
        data = {}
        for ziel in self.ziele:
            data.update(meilenstein_formset_data(f"ziel{ziel.id}"))
        for key in list(data):
            if key.startswith(f"ziel{self.ziele[0].id}-2-"):
                data[key] = ""
        response = self.client.post(reverse("accounts:onboarding-meilensteine"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Meilenstein.objects.count(), 0)

    def test_already_having_three_per_goal_skips_to_dashboard(self):
        today = timezone.localdate()
        for ziel in self.ziele:
            for i in range(3):
                Meilenstein.objects.create(
                    jahresziel=ziel, title=f"M{i}", description="x", deadline=today + timedelta(days=50)
                )
        response = self.client.get(reverse("accounts:onboarding-meilensteine"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dailydash:today"))
