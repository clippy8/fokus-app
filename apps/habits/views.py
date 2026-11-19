from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.dailydash.services import get_or_create_day

from .forms import HabitForm
from .models import DailyHabitCheck, Habit, WeeklyHabitCheck


@login_required
def habit_list(request):
    today = timezone.localdate()
    iso_year, iso_week, _ = today.isocalendar()
    day = get_or_create_day(request.user, today)

    habits = Habit.objects.filter(user=request.user, active=True)
    daily_habits = []
    weekly_habits = []
    for habit in habits:
        if habit.frequency == Habit.DAILY:
            checked = DailyHabitCheck.objects.filter(habit=habit, day=day).exists()
            daily_habits.append({"habit": habit, "checked": checked})
        else:
            checked = WeeklyHabitCheck.objects.filter(habit=habit, iso_year=iso_year, iso_week=iso_week).exists()
            weekly_habits.append({"habit": habit, "checked": checked})

    context = {
        "daily_habits": daily_habits,
        "weekly_habits": weekly_habits,
        "today": today.isoformat(),
        "iso_year": iso_year,
        "iso_week": iso_week,
    }
    return render(request, "habits/habit_list.html", context)


@require_POST
@login_required
def toggle_daily(request, pk, date):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    parsed_date = timezone.datetime.fromisoformat(date).date()
    day = get_or_create_day(request.user, parsed_date)
    check, created = DailyHabitCheck.objects.get_or_create(habit=habit, day=day)
    if not created:
        check.delete()
        checked = False
    else:
        checked = True
    return render(request, "habits/_daily_habit_row.html", {"habit": habit, "checked": checked, "date": date})


@require_POST
@login_required
def toggle_weekly(request, pk, iso_year, iso_week):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    check, created = WeeklyHabitCheck.objects.get_or_create(habit=habit, iso_year=iso_year, iso_week=iso_week)
    if not created:
        check.delete()
        checked = False
    else:
        checked = True
    return render(
        request,
        "habits/_weekly_habit_row.html",
        {"habit": habit, "checked": checked, "iso_year": iso_year, "iso_week": iso_week},
    )


@login_required
def habit_add(request):
    if request.method == "POST":
        form = HabitForm(request.POST, instance=Habit(user=request.user))
        if form.is_valid():
            try:
                form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                return redirect("habits:list")
    else:
        form = HabitForm()
    return render(request, "habits/habit_form.html", {"form": form})


@login_required
def habit_edit(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            try:
                form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                return redirect("habits:list")
    else:
        form = HabitForm(instance=habit)
    return render(request, "habits/habit_form.html", {"form": form, "habit": habit})


@require_POST
@login_required
def habit_deactivate(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    habit.active = False
    habit.save()
    messages.success(request, f"Habit '{habit.name}' deaktiviert.")
    return redirect("habits:list")
