import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
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


def make_meilenstein(jahresziel, title, **overrides):
    today = timezone.localdate()
    defaults = {
        "jahresziel": jahresziel,
        "title": title,
        "description": "Konkrete Beschreibung des Meilensteins.",
        "deadline": today + timedelta(days=100),
    }
    defaults.update(overrides)
    return Meilenstein.objects.create(**defaults)


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

    def test_progress_percent_works_for_decreasing_goal(self):
        # Zielgewicht erreichen: Start 100 kg, Ziel 70 kg — der Zielwert ist kleiner als der Startwert.
        ziel = make_ziel(self.user, "Zielgewicht erreichen", start_value=100, current_value=100, target_value=70)
        self.assertEqual(ziel.progress_percent, 0)
        ziel.current_value = 85
        ziel.save()
        self.assertEqual(ziel.progress_percent, 50)
        ziel.current_value = 70
        ziel.save()
        self.assertEqual(ziel.progress_percent, 100)
        ziel.current_value = 65
        ziel.save()
        self.assertEqual(ziel.progress_percent, 100)
        ziel.current_value = 105
        ziel.save()
        self.assertEqual(ziel.progress_percent, 0)

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
            make_meilenstein(self.ziel, f"M{i}")
        with self.assertRaises(ValidationError):
            make_meilenstein(self.ziel, "M4")

    def test_default_status_is_not_started(self):
        meilenstein = make_meilenstein(self.ziel, "M1")
        self.assertEqual(meilenstein.status, Meilenstein.NOT_STARTED)


class MeilensteinProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.ziel = make_ziel(self.user, "Ziel")

    def test_progress_percent_uses_start_stand_target(self):
        meilenstein = make_meilenstein(self.ziel, "M1", start_value=0, current_value=5, target_value=10)
        self.assertEqual(meilenstein.progress_percent, 50)

    def test_progress_percent_works_for_decreasing_goal(self):
        meilenstein = make_meilenstein(self.ziel, "Abnehmen", start_value=100, current_value=85, target_value=70)
        self.assertEqual(meilenstein.progress_percent, 50)

    def test_progress_percent_clamped_to_100(self):
        meilenstein = make_meilenstein(self.ziel, "M1", start_value=0, current_value=15, target_value=10)
        self.assertEqual(meilenstein.progress_percent, 100)

    def test_progress_percent_zero_span(self):
        meilenstein = make_meilenstein(self.ziel, "M1", start_value=5, current_value=5, target_value=5)
        self.assertEqual(meilenstein.progress_percent, 100)


class ProjectWeekFocusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        ziel = make_ziel(self.user, "Ziel")
        self.meilenstein = make_meilenstein(ziel, "M1")
        self.projekt = Projekt.objects.create(meilenstein=self.meilenstein, title="P1")

    def test_focused_this_week_vs_last_week(self):
        iso_year, iso_week, _ = timezone.localdate().isocalendar()
        ProjectWeekFocus.objects.create(projekt=self.projekt, iso_year=iso_year, iso_week=iso_week)
        self.assertTrue(self.projekt.is_focused_in(iso_year, iso_week))
        self.assertFalse(self.projekt.is_focused_in(iso_year, iso_week + 1 if iso_week < 52 else 1))


class ProjektStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        ziel = make_ziel(self.user, "Ziel")
        self.meilenstein = make_meilenstein(ziel, "M1")

    def test_default_status_is_not_started(self):
        projekt = Projekt.objects.create(meilenstein=self.meilenstein, title="P1")
        self.assertEqual(projekt.status, Projekt.NOT_STARTED)

    def test_status_choices_are_german_and_cover_the_five_states(self):
        labels = dict(Projekt.STATUS_CHOICES)
        self.assertEqual(labels[Projekt.NOT_STARTED], "Nicht begonnen")
        self.assertEqual(labels[Projekt.ON_HOLD], "Pausiert")
        self.assertEqual(labels[Projekt.ACTIVE], "Aktiv")
        self.assertEqual(labels[Projekt.COMPLETED], "Abgeschlossen")
        self.assertEqual(labels[Projekt.ABANDONED], "Verworfen")


class ProjektTimelineViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)
        self.ziel = make_ziel(self.user, "Ziel")
        self.meilenstein = make_meilenstein(self.ziel, "M1")
        self.today = timezone.localdate()

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("goals:projekt-timeline"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_splits_scheduled_and_unscheduled_projects(self):
        scheduled = Projekt.objects.create(
            meilenstein=self.meilenstein,
            title="Geplant",
            start_date=self.today,
            end_date=self.today + timedelta(days=10),
        )
        unscheduled = Projekt.objects.create(meilenstein=self.meilenstein, title="Ungeplant")
        response = self.client.get(reverse("goals:projekt-timeline"))
        self.assertEqual(response.status_code, 200)
        bar_ids = [bar["projekt"].id for bar in response.context["bars"]]
        self.assertEqual(bar_ids, [scheduled.id])
        self.assertEqual([p.id for p in response.context["unscheduled"]], [unscheduled.id])

    def test_bar_position_matches_dates(self):
        projekt = Projekt.objects.create(
            meilenstein=self.meilenstein,
            title="Geplant",
            start_date=self.today,
            end_date=self.today + timedelta(days=5),
        )
        response = self.client.get(reverse("goals:projekt-timeline"))
        bar = response.context["bars"][0]
        window_start = response.context["window_start"]
        px_per_day = response.context["px_per_day"]
        self.assertEqual(bar["left_px"], (projekt.start_date - window_start).days * px_per_day)
        self.assertEqual(bar["width_px"], 5 * px_per_day)


class ProjektUpdateDatesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)
        ziel = make_ziel(self.user, "Ziel")
        self.meilenstein = make_meilenstein(ziel, "M1")
        self.projekt = Projekt.objects.create(meilenstein=self.meilenstein, title="P1")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse("goals:projekt-update-dates", kwargs={"pk": self.projekt.pk}),
            {"start_date": "2026-01-01", "end_date": "2026-01-10"},
        )
        self.assertEqual(response.status_code, 302)

    def test_sets_dates_from_scratch(self):
        response = self.client.post(
            reverse("goals:projekt-update-dates", kwargs={"pk": self.projekt.pk}),
            {"start_date": "2026-03-01", "end_date": "2026-03-10"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["ok"])
        self.projekt.refresh_from_db()
        self.assertEqual(self.projekt.start_date.isoformat(), "2026-03-01")
        self.assertEqual(self.projekt.end_date.isoformat(), "2026-03-10")

    def test_rejects_end_before_start(self):
        response = self.client.post(
            reverse("goals:projekt-update-dates", kwargs={"pk": self.projekt.pk}),
            {"start_date": "2026-03-10", "end_date": "2026-03-01"},
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["ok"])
        self.projekt.refresh_from_db()
        self.assertIsNone(self.projekt.start_date)

    def test_other_users_project_is_not_reachable(self):
        other_user = User.objects.create_user(username="bob", password="pw")
        other_ziel = make_ziel(other_user, "Anderes Ziel")
        other_meilenstein = make_meilenstein(other_ziel, "Anderer Meilenstein")
        other_projekt = Projekt.objects.create(meilenstein=other_meilenstein, title="Fremdes Projekt")
        response = self.client.post(
            reverse("goals:projekt-update-dates", kwargs={"pk": other_projekt.pk}),
            {"start_date": "2026-03-01", "end_date": "2026-03-10"},
        )
        self.assertEqual(response.status_code, 404)

    def test_can_clear_dates(self):
        self.projekt.start_date = timezone.localdate()
        self.projekt.end_date = timezone.localdate() + timedelta(days=5)
        self.projekt.save()
        response = self.client.post(
            reverse("goals:projekt-update-dates", kwargs={"pk": self.projekt.pk}),
            {"start_date": "", "end_date": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.projekt.refresh_from_db()
        self.assertIsNone(self.projekt.start_date)
        self.assertIsNone(self.projekt.end_date)


class DateWidgetIsoFormatTests(TestCase):
    """
    HTML5 <input type="date"> requires its value attribute in ISO format
    (YYYY-MM-DD) to be recognized by the browser, regardless of UI locale. With
    LANGUAGE_CODE="de-de", Django's DateInput widget otherwise renders existing
    values in German format (DD.MM.YYYY) when pre-filling an edit form, which the
    browser then silently fails to parse — the field just shows up empty. These
    tests assert every such widget explicitly requests the ISO format.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)
        self.ziel = make_ziel(
            self.user, "Ziel", start_date=timezone.localdate(), end_date=timezone.localdate() + timedelta(days=100)
        )
        self.meilenstein = make_meilenstein(
            self.ziel, "M1", deadline=timezone.localdate() + timedelta(days=50)
        )
        self.projekt = Projekt.objects.create(
            meilenstein=self.meilenstein,
            title="P1",
            start_date=timezone.localdate(),
            end_date=timezone.localdate() + timedelta(days=5),
        )

    def test_jahresziel_edit_prefills_iso_dates(self):
        response = self.client.get(reverse("goals:jahresziel-edit", kwargs={"pk": self.ziel.pk}))
        self.assertContains(response, f'value="{self.ziel.start_date.isoformat()}"')
        self.assertContains(response, f'value="{self.ziel.end_date.isoformat()}"')

    def test_meilenstein_edit_prefills_iso_date(self):
        response = self.client.get(reverse("goals:meilenstein-edit", kwargs={"pk": self.meilenstein.pk}))
        self.assertContains(response, f'value="{self.meilenstein.deadline.isoformat()}"')

    def test_projekt_edit_prefills_iso_dates(self):
        response = self.client.get(reverse("goals:projekt-edit", kwargs={"pk": self.projekt.pk}))
        self.assertContains(response, f'value="{self.projekt.start_date.isoformat()}"')
        self.assertContains(response, f'value="{self.projekt.end_date.isoformat()}"')
