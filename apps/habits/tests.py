from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.dailydash.services import get_or_create_day

from .models import DailyHabitCheck, Habit


class HabitMaxActiveTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_sixth_active_habit_raises(self):
        for i in range(5):
            Habit.objects.create(user=self.user, name=f"Habit {i}", frequency=Habit.DAILY)
        with self.assertRaises(ValidationError):
            Habit.objects.create(user=self.user, name="Habit 6", frequency=Habit.DAILY)

    def test_inactive_habits_dont_count(self):
        for i in range(5):
            Habit.objects.create(user=self.user, name=f"Habit {i}", frequency=Habit.DAILY)
        Habit.objects.filter(user=self.user).first().delete()
        # recreate one as inactive, should still allow a new active one
        habit = Habit(user=self.user, name="Inactive", frequency=Habit.DAILY, active=False)
        habit.save()
        Habit.objects.create(user=self.user, name="New active", frequency=Habit.DAILY)


class ToggleDailyViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pw")
        self.client.force_login(self.user)
        self.habit = Habit.objects.create(user=self.user, name="Liegestütze", frequency=Habit.DAILY)
        self.today = timezone.localdate()

    def test_toggle_creates_and_removes_check(self):
        url = reverse("habits:toggle-daily", kwargs={"pk": self.habit.pk, "date": self.today.isoformat()})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        day = get_or_create_day(self.user, self.today)
        self.assertTrue(DailyHabitCheck.objects.filter(habit=self.habit, day=day).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DailyHabitCheck.objects.filter(habit=self.habit, day=day).exists())
