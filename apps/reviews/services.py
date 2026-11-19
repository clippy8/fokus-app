from django.utils import timezone

from apps.dailydash.models import Day
from apps.goals.models import Meilenstein, Projekt, ProjectWeekFocus
from apps.habits.models import DailyHabitCheck, Habit, WeeklyHabitCheck

from .isoweek_utils import previous_iso_week, week_date_range
from .models import WeeklyReview


def get_or_create_review(user, iso_year, iso_week):
    review, _ = WeeklyReview.objects.get_or_create(user=user, iso_year=iso_year, iso_week=iso_week)
    return review


def get_or_create_current_review(user):
    iso_year, iso_week, _ = timezone.localdate().isocalendar()
    return get_or_create_review(user, iso_year, iso_week), iso_year, iso_week


def aggregate_week_data(user, iso_year, iso_week):
    start, end = week_date_range(iso_year, iso_week)
    days = Day.objects.filter(user=user, date__range=(start, end))
    days_count = days.count()

    daily_summary = []
    for habit in Habit.objects.filter(user=user, frequency=Habit.DAILY):
        checked_count = DailyHabitCheck.objects.filter(habit=habit, day__in=days).count()
        daily_summary.append({"habit": habit, "checked": checked_count, "total": days_count})

    weekly_summary = []
    for habit in Habit.objects.filter(user=user, frequency=Habit.WEEKLY):
        checked = WeeklyHabitCheck.objects.filter(habit=habit, iso_year=iso_year, iso_week=iso_week).exists()
        weekly_summary.append({"habit": habit, "checked": checked})

    meilensteine = Meilenstein.objects.filter(jahresziel__user=user).exclude(jahresziel__status="archived")

    projekte_calendar = Projekt.objects.filter(
        meilenstein__jahresziel__user=user, end_date__isnull=False
    ).exclude(status=Projekt.ARCHIVED).order_by("end_date")

    focus_this_week = set(
        Projekt.objects.filter(
            meilenstein__jahresziel__user=user,
            week_focus_entries__iso_year=iso_year,
            week_focus_entries__iso_week=iso_week,
        ).values_list("id", flat=True)
    )
    prev_year, prev_week = previous_iso_week(iso_year, iso_week)
    focus_last_week = set(
        Projekt.objects.filter(
            meilenstein__jahresziel__user=user,
            week_focus_entries__iso_year=prev_year,
            week_focus_entries__iso_week=prev_week,
        ).values_list("id", flat=True)
    )
    all_focus_ids = focus_this_week | focus_last_week
    projekte_focus = Projekt.objects.filter(id__in=all_focus_ids)

    return {
        "week_start": start,
        "week_end": end,
        "daily_summary": daily_summary,
        "weekly_summary": weekly_summary,
        "meilensteine": meilensteine,
        "projekte_calendar": projekte_calendar,
        "projekte_focus_this_week": [p for p in projekte_focus if p.id in focus_this_week],
        "projekte_focus_last_week": [p for p in projekte_focus if p.id in focus_last_week],
    }
