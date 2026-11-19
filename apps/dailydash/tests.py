from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Day, DayRoutineCheck, RoutineItem
from .services import get_or_create_day


class GetOrCreateDayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.today = timezone.localdate()

    def test_idempotent(self):
        day1 = get_or_create_day(self.user, self.today)
        day2 = get_or_create_day(self.user, self.today)
        self.assertEqual(day1.pk, day2.pk)
        self.assertEqual(Day.objects.filter(user=self.user, date=self.today).count(), 1)

    def test_new_routine_item_not_added_retroactively_to_past_day(self):
        past_date = self.today - timedelta(days=10)
        day = get_or_create_day(self.user, past_date)
        self.assertEqual(day.routine_checks.count(), 0)

        RoutineItem.objects.create(user=self.user, name="Liegestütze", timing=RoutineItem.MORNING)

        day_again = get_or_create_day(self.user, past_date)
        self.assertEqual(day_again.routine_checks.count(), 0)

    def test_routine_item_added_for_today_and_future(self):
        RoutineItem.objects.create(user=self.user, name="Wasser trinken", timing=RoutineItem.MORNING)
        day = get_or_create_day(self.user, self.today)
        self.assertEqual(day.routine_checks.count(), 1)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def test_requires_login(self):
        response = self.client.get(reverse("dailydash:today"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_toggle_flips_checked_state(self):
        user = User.objects.create_user(username="bob", password="pw")
        self.client.force_login(user)
        day = get_or_create_day(user, self.today)
        item = RoutineItem.objects.create(user=user, name="Test", timing=RoutineItem.MORNING)
        check = DayRoutineCheck.objects.create(day=day, routine_item=item)
        response = self.client.post(
            reverse("dailydash:routine-check-toggle", kwargs={"date": self.today.isoformat(), "check_id": check.pk})
        )
        self.assertEqual(response.status_code, 200)
        check.refresh_from_db()
        self.assertTrue(check.checked)
