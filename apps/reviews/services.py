from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from apps.dailydash.models import Day
from apps.dokumente.models import Dokument
from apps.fitness.models import FoodLogEntry, WorkoutSet
from apps.goals.models import Jahresziel, Meilenstein, Projekt, ProjectWeekFocus
from apps.habits.models import DailyHabitCheck, Habit, WeeklyHabitCheck

from .isoweek_utils import previous_iso_week, week_date_range
from .models import WeeklyReview

WEEKDAY_ABBR = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def get_or_create_review(user, iso_year, iso_week):
    review, _ = WeeklyReview.objects.get_or_create(user=user, iso_year=iso_year, iso_week=iso_week)
    return review


def get_or_create_current_review(user):
    iso_year, iso_week, _ = timezone.localdate().isocalendar()
    return get_or_create_review(user, iso_year, iso_week), iso_year, iso_week


def aggregate_week_data(user, iso_year, iso_week):
    start, end = week_date_range(iso_year, iso_week)
    days = Day.objects.filter(user=user, date__range=(start, end))

    week_days = [start + timedelta(days=i) for i in range(7)]
    week_day_labels = [f"{WEEKDAY_ABBR[i]} {d.strftime('%d.%m.')}" for i, d in enumerate(week_days)]

    daily_summary = []
    for habit in Habit.objects.filter(user=user, frequency=Habit.DAILY):
        checked_dates = set(
            DailyHabitCheck.objects.filter(habit=habit, day__in=days).values_list("day__date", flat=True)
        )
        daily_summary.append({"habit": habit, "checks": [d in checked_dates for d in week_days]})

    weekly_summary = []
    for habit in Habit.objects.filter(user=user, frequency=Habit.WEEKLY):
        checked = WeeklyHabitCheck.objects.filter(habit=habit, iso_year=iso_year, iso_week=iso_week).exists()
        weekly_summary.append({"habit": habit, "checked": checked})

    notizen = Dokument.objects.filter(user=user, type=Dokument.NOTIZ)

    jahresziele = Jahresziel.objects.filter(user=user, archived=False)

    meilensteine = Meilenstein.objects.filter(jahresziel__user=user, jahresziel__archived=False)

    projekte_calendar = Projekt.objects.filter(
        meilenstein__jahresziel__user=user, end_date__isnull=False
    ).exclude(status=Projekt.ABANDONED).order_by("end_date")

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

    food_by_date = defaultdict(list)
    for entry in FoodLogEntry.objects.filter(user=user, day__in=days).select_related("day").order_by("day__date", "created_at"):
        food_by_date[entry.day.date].append(entry.name)

    workout_counts_by_date = defaultdict(dict)
    workout_order_by_date = defaultdict(list)
    for workout_set in (
        WorkoutSet.objects.filter(user=user, day__in=days)
        .select_related("day", "exercise")
        .order_by("day__date", "exercise__name", "set_number")
    ):
        d = workout_set.day.date
        name = workout_set.exercise.name
        if name not in workout_counts_by_date[d]:
            workout_counts_by_date[d][name] = 0
            workout_order_by_date[d].append(name)
        workout_counts_by_date[d][name] += 1

    fitness_week = {
        "food": [food_by_date.get(d, []) for d in week_days],
        "workout": [
            [f"{name} ({workout_counts_by_date[d][name]}x)" for name in workout_order_by_date.get(d, [])]
            for d in week_days
        ],
    }

    return {
        "week_start": start,
        "week_end": end,
        "week_day_labels": week_day_labels,
        "daily_summary": daily_summary,
        "fitness_week": fitness_week,
        "weekly_summary": weekly_summary,
        "notizen": notizen,
        "jahresziele": jahresziele,
        "meilensteine": meilensteine,
        "projekte_calendar": projekte_calendar,
        "projekte_focus_this_week": [p for p in projekte_focus if p.id in focus_this_week],
        "projekte_focus_last_week": [p for p in projekte_focus if p.id in focus_last_week],
    }
