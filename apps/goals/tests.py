from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt


class JahreszielLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_max_3_per_year(self):
        for i in range(3):
            Jahresziel.objects.create(user=self.user, title=f"Ziel {i}", year=2026)
        with self.assertRaises(ValidationError):
            Jahresziel.objects.create(user=self.user, title="Ziel 4", year=2026)

    def test_archived_goals_dont_count(self):
        for i in range(3):
            Jahresziel.objects.create(user=self.user, title=f"Ziel {i}", year=2026)
        ziel = Jahresziel.objects.filter(user=self.user, year=2026).first()
        ziel.status = Jahresziel.ARCHIVED
        ziel.save()
        Jahresziel.objects.create(user=self.user, title="Ziel 4", year=2026)


class MeilensteinLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.ziel = Jahresziel.objects.create(user=self.user, title="Ziel", year=2026)

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
        ziel = Jahresziel.objects.create(user=self.user, title="Ziel", year=2026)
        self.meilenstein = Meilenstein.objects.create(jahresziel=ziel, title="M1")
        self.projekt = Projekt.objects.create(meilenstein=self.meilenstein, title="P1")

    def test_focused_this_week_vs_last_week(self):
        iso_year, iso_week, _ = timezone.localdate().isocalendar()
        ProjectWeekFocus.objects.create(projekt=self.projekt, iso_year=iso_year, iso_week=iso_week)
        self.assertTrue(self.projekt.is_focused_in(iso_year, iso_week))
        self.assertFalse(self.projekt.is_focused_in(iso_year, iso_week + 1 if iso_week < 52 else 1))
