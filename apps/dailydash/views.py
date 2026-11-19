from datetime import date as date_cls
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RoutineItemForm
from .models import Day, DayRoutineCheck, RoutineItem
from .services import get_or_create_day


@login_required
def today(request):
    return redirect("dailydash:day-detail", date=timezone.localdate().isoformat())


@login_required
def day_detail(request, date):
    parsed_date = date_cls.fromisoformat(date)
    day = get_or_create_day(request.user, parsed_date)
    morning_checks = day.routine_checks.filter(routine_item__timing=RoutineItem.MORNING)
    evening_checks = day.routine_checks.filter(routine_item__timing=RoutineItem.EVENING)
    context = {
        "day": day,
        "morning_checks": morning_checks,
        "evening_checks": evening_checks,
        "is_today": parsed_date == timezone.localdate(),
        "prev_date": (parsed_date - timedelta(days=1)).isoformat(),
        "next_date": (parsed_date + timedelta(days=1)).isoformat(),
    }
    return render(request, "dailydash/day_detail.html", context)


@login_required
def history_list(request):
    days = Day.objects.filter(user=request.user).order_by("-date")[:90]
    return render(request, "dailydash/history_list.html", {"days": days})


@require_POST
@login_required
def toggle_routine_check(request, date, check_id):
    check = get_object_or_404(
        DayRoutineCheck, pk=check_id, day__user=request.user, day__date=date_cls.fromisoformat(date)
    )
    check.checked = not check.checked
    check.checked_at = timezone.now() if check.checked else None
    check.save()
    return render(request, "dailydash/_routine_check_row.html", {"check": check, "date": date})


@require_POST
@login_required
def save_journal(request, date):
    day = get_object_or_404(Day, user=request.user, date=date_cls.fromisoformat(date))
    day.journal_text = request.POST.get("journal_text", "")
    day.save()
    return render(request, "dailydash/_journal_save_status.html", {"saved_at": timezone.now()})


@login_required
def routine_item_list(request):
    items = RoutineItem.objects.filter(user=request.user)
    return render(request, "dailydash/routine_item_list.html", {"items": items})


@login_required
def routine_item_add(request):
    if request.method == "POST":
        form = RoutineItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect("dailydash:routine-item-list")
    else:
        form = RoutineItemForm()
    return render(request, "dailydash/routine_item_form.html", {"form": form})


@login_required
def routine_item_edit(request, pk):
    item = get_object_or_404(RoutineItem, pk=pk, user=request.user)
    if request.method == "POST":
        form = RoutineItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("dailydash:routine-item-list")
    else:
        form = RoutineItemForm(instance=item)
    return render(request, "dailydash/routine_item_form.html", {"form": form, "item": item})


@require_POST
@login_required
def routine_item_deactivate(request, pk):
    item = get_object_or_404(RoutineItem, pk=pk, user=request.user)
    item.active = False
    item.save()
    return redirect("dailydash:routine-item-list")
