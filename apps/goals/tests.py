from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt


def make_ziel(user, title, **overrides):
    today = timezone.localdate()
    defaults = {
        "user": user,
        "title": title,
        "description": "Konkrete Beschreibung des Ziels.",
        "start_date": today,
        "end_date": today + timedelta(days=365),
    }
    defaults.update(overrides)
    return Jahresziel.objects.create(**defaults)


class JahreszielLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_max_3_active(self):
        for i in range(3):
            make_ziel(self.user, f"Ziel {i}")
        with self.assertRaises(ValidationError):
            make_ziel(self.user, "Ziel 4")

    def test_archived_goals_dont_count(self):
        for i in range(3):
            make_ziel(self.user, f"Ziel {i}")
        ziel = Jahresziel.objects.filter(user=self.user).first()
        ziel.archived = True
        ziel.save()
        make_ziel(self.user, "Ziel 4")

    def test_end_date_must_be_after_start_date(self):
        today = timezone.localdate()
        with self.assertRaises(ValidationError):
            make_ziel(self.user, "Invalid", start_date=today, end_date=today - timedelta(days=1))


class JahreszielProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_progress_percent_uses_start_stand_target(self):
        ziel = make_ziel(self.user, "Einkommen verdoppeln", start_value=1500, current_value=2000, target_value=3000)
        self.assertEqual(ziel.progress_percent, 33)

    def test_progress_percent_clamped_to_100(self):
        ziel = make_ziel(self.user, "Überschritten", start_value=0, current_value=150, target_value=100)
        self.assertEqual(ziel.progress_percent, 100)

    def test_progress_percent_zero_span_defaults_to_status(self):
        ziel = make_ziel(self.user, "Kein Unterschied", start_value=5, current_value=5, target_value=5)
        self.assertEqual(ziel.progress_percent, 0)
        ziel.status = Jahresziel.ACHIEVED
        ziel.save()
        self.assertEqual(ziel.progress_percent, 100)

    def test_time_percent(self):
        today = timezone.localdate()
        ziel = make_ziel(
            self.user, "Halbzeit", start_date=today - timedelta(days=100), end_date=today + timedelta(days=100)
        )
        self.assertEqual(ziel.time_percent, 50)


class MeilensteinLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.ziel = make_ziel(self.user, "Ziel")

    def test_max_3_per_jahresziel(self):
        for i in range(3):
            Meilenstein.objects.create(jahresziel=self.ziel, title=f"M{i}")
        with self.assertRaises(ValidationError):
            Meilenstein.objects.create(jahresziel=self.ziel, title="M4")

    def test_progress_percent(self):
        meilenstein = Meilenstein.objects.create(jahresziel=self.ziel, title="M1")
        for i in range(4):
            Projekt.objects.create(meilenstein=meilenstein, title=f"P{i}")
        done_projekte = meilenstein.projekte.all()[:2]
        for p in done_projekte:
            p.status = Projekt.DONE
            p.save()
        self.assertEqual(meilenstein.progress_percent, 50)

    def test_progress_percent_no_projects(self):
        meilenstein = Meilenstein.objects.create(jahresziel=self.ziel, title="M1")
        self.assertEqual(meilenstein.progress_percent, 0)


class ProjectWeekFocusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        ziel = make_ziel(self.user, "Ziel")
        self.meilenstein = Meilenstein.objects.create(jahresziel=ziel, title="M1")
        self.projekt = Projekt.objects.create(meilenstein=self.meilenstein, title="P1")

    def test_focused_this_week_vs_last_week(self):
        iso_year, iso_week, _ = timezone.localdate().isocalendar()
        ProjectWeekFocus.objects.create(projekt=self.projekt, iso_year=iso_year, iso_week=iso_week)
        self.assertTrue(self.projekt.is_focused_in(iso_year, iso_week))
        self.assertFalse(self.projekt.is_focused_in(iso_year, iso_week + 1 if iso_week < 52 else 1))
