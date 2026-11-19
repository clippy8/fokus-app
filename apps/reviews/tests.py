from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .isoweek_utils import previous_iso_week, week_date_range
from .models import WeeklyReview
from .services import get_or_create_review


class IsoWeekUtilsTests(TestCase):
    def test_week_date_range_monday_start(self):
        start, end = week_date_range(2026, 1)
        self.assertEqual(start.weekday(), 0)
        self.assertEqual((end - start).days, 6)

    def test_previous_iso_week_across_year_boundary(self):
        # 2026-01-01 is a Thursday, ISO week 1 of 2026
        iso_year, iso_week, _ = date(2026, 1, 1).isocalendar()
        prev_year, prev_week = previous_iso_week(iso_year, iso_week)
        self.assertEqual((prev_year, prev_week), (2025, 52))

    def test_previous_iso_week_normal_case(self):
        prev_year, prev_week = previous_iso_week(2026, 10)
        self.assertEqual((prev_year, prev_week), (2026, 9))


class WeeklyReviewServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_get_or_create_review_idempotent(self):
        review1 = get_or_create_review(self.user, 2026, 47)
        review2 = get_or_create_review(self.user, 2026, 47)
        self.assertEqual(review1.pk, review2.pk)
        self.assertEqual(WeeklyReview.objects.filter(user=self.user, iso_year=2026, iso_week=47).count(), 1)
