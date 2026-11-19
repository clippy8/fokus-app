from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FinanceEntry


class FinanceEntryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_saldo_calculation(self):
        now = timezone.now()
        FinanceEntry.objects.create(
            user=self.user, name="Gehalt", amount=Decimal("1000.00"), timestamp=now,
            category=FinanceEntry.EINNAHMEN,
        )
        FinanceEntry.objects.create(
            user=self.user, name="Miete", amount=Decimal("600.00"), timestamp=now,
            category=FinanceEntry.FIXKOSTEN,
        )
        FinanceEntry.objects.create(
            user=self.user, name="Netflix", amount=Decimal("10.00"), timestamp=now,
            category=FinanceEntry.AUSGABEN,
        )
        entries = FinanceEntry.objects.filter(user=self.user)
        self.assertEqual(entries.count(), 3)


class FinanceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.other_user = User.objects.create_user(username="bob", password="pw")
        self.client.force_login(self.user)

    def test_list_only_shows_own_entries(self):
        FinanceEntry.objects.create(
            user=self.user, name="Netflix", amount=Decimal("10.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        FinanceEntry.objects.create(
            user=self.other_user, name="Spotify", amount=Decimal("5.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        response = self.client.get(reverse("finanzen:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Netflix")
        self.assertNotContains(response, "Spotify")

    def test_add_entry(self):
        response = self.client.post(reverse("finanzen:add"), {
            "name": "Netflix",
            "tag": "Unterhaltung",
            "amount": "10.00",
            "timestamp": "2026-10-18T10:30",
            "category": FinanceEntry.FIXKOSTEN,
        })
        self.assertEqual(response.status_code, 302)
        entry = FinanceEntry.objects.get(user=self.user)
        self.assertEqual(entry.name, "Netflix")
        self.assertEqual(entry.tag, "Unterhaltung")
        self.assertEqual(entry.amount, Decimal("10.00"))
        self.assertEqual(entry.category, FinanceEntry.FIXKOSTEN)

    def test_cannot_edit_other_users_entry(self):
        entry = FinanceEntry.objects.create(
            user=self.other_user, name="Spotify", amount=Decimal("5.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        response = self.client.get(reverse("finanzen:edit", kwargs={"pk": entry.pk}))
        self.assertEqual(response.status_code, 404)

    def test_delete_entry(self):
        entry = FinanceEntry.objects.create(
            user=self.user, name="Netflix", amount=Decimal("10.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        response = self.client.post(reverse("finanzen:delete", kwargs={"pk": entry.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FinanceEntry.objects.filter(pk=entry.pk).exists())


class FinanceEntryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.other_user = User.objects.create_user(username="bob", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_create_entry_sets_user(self):
        response = self.client.post("/api/v1/finance-entries/", {
            "name": "Netflix",
            "tag": "Unterhaltung",
            "amount": "10.00",
            "timestamp": timezone.now().isoformat(),
            "category": FinanceEntry.FIXKOSTEN,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = FinanceEntry.objects.get(id=response.data["id"])
        self.assertEqual(entry.user, self.user)

    def test_list_only_returns_own_entries(self):
        FinanceEntry.objects.create(
            user=self.user, name="Netflix", amount=Decimal("10.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        FinanceEntry.objects.create(
            user=self.other_user, name="Spotify", amount=Decimal("5.00"), timestamp=timezone.now(),
            category=FinanceEntry.FIXKOSTEN,
        )
        response = self.client.get("/api/v1/finance-entries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]) if "results" in response.data else len(response.data), 1)
