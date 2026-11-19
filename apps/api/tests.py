from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from apps.dailydash.models import Day
from apps.habits.models import Habit


class ApiAuthTests(APITestCase):
    def test_unauthenticated_request_rejected(self):
        response = self.client.get("/api/v1/days/today/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ApiUserScopingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.other_user = User.objects.create_user(username="bob", password="pw")
        Day.objects.create(user=self.other_user, date="2026-01-01")
        self.client.force_authenticate(user=self.user)

    def test_user_only_sees_own_days(self):
        Day.objects.create(user=self.user, date="2026-01-02")
        response = self.client.get("/api/v1/days/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [d["date"] for d in response.data]
        self.assertEqual(dates, ["2026-01-02"])


class ApiCrudRoundtripTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_habit_create_and_retrieve(self):
        response = self.client.post(
            "/api/v1/habits/", {"name": "Liegestütze", "frequency": "daily"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit_id = response.data["id"]
        response = self.client.get(f"/api/v1/habits/{habit_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Liegestütze")

    def test_jahresziel_create_and_retrieve(self):
        response = self.client.post(
            "/api/v1/jahresziele/",
            {
                "title": "Sportlich werden",
                "description": "100 Liegestütze am Stück schaffen.",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "start_value": 0,
                "target_value": 100,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ziel_id = response.data["id"]
        response = self.client.get(f"/api/v1/jahresziele/{ziel_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Sportlich werden")

    def test_todo_create_and_retrieve(self):
        response = self.client.post("/api/v1/todos/", {"title": "Laufschuhe kaufen"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        todo_id = response.data["id"]
        response = self.client.get(f"/api/v1/todos/{todo_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Laufschuhe kaufen")

    def test_habit_max_5_validation_via_api_returns_400(self):
        for i in range(5):
            Habit.objects.create(user=self.user, name=f"Habit {i}", frequency=Habit.DAILY)
        response = self.client.post(
            "/api/v1/habits/", {"name": "Habit 6", "frequency": "daily"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
