from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import JahreszielForm, MeilensteinForm, ProjektForm, TodoForm
from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt, Todo

TIMELINE_DEFAULT_DURATION_DAYS = 7
PX_PER_DAY = 24


@login_required
def jahresziel_list(request):
    jahresziele = (
        Jahresziel.objects.filter(user=request.user, archived=False)
        .prefetch_related("meilensteine__projekte")
    )
    iso_year, iso_week, _ = timezone.localdate().isocalendar()
    focused_ids = set(
        ProjectWeekFocus.objects.filter(
            iso_year=iso_year, iso_week=iso_week, projekt__meilenstein__jahresziel__user=request.user
        ).values_list("projekt_id", flat=True)
    )
    context = {"jahresziele": jahresziele, "focused_ids": focused_ids}
    return render(request, "goals/jahresziel_list.html", context)


@login_required
def jahresziel_add(request):
    if request.method == "POST":
        form = JahreszielForm(request.POST, instance=Jahresziel(user=request.user))
        if form.is_valid():
            try:
                form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                return redirect("goals:list")
    else:
        form = JahreszielForm()
    return render(request, "goals/jahresziel_form.html", {"form": form})


@login_required
def jahresziel_edit(request, pk):
    ziel = get_object_or_404(Jahresziel, pk=pk, user=request.user)
    if request.method == "POST":
        form = JahreszielForm(request.POST, instance=ziel)
        if form.is_valid():
            try:
                form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                return redirect("goals:list")
    else:
        form = JahreszielForm(instance=ziel)
    return render(request, "goals/jahresziel_form.html", {"form": form, "ziel": ziel})


@require_POST
@login_required
def jahresziel_archive(request, pk):
    ziel = get_object_or_404(Jahresziel, pk=pk, user=request.user)
    ziel.archived = True
    ziel.save()
    return redirect("goals:list")


@login_required
def meilenstein_add(request, jahresziel_pk):
    ziel = get_object_or_404(Jahresziel, pk=jahresziel_pk, user=request.user)
    if request.method == "POST":
        form = MeilensteinForm(request.POST, instance=Meilenstein(jahresziel=ziel))
        if form.is_valid():
            try:
                form.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                return redirect("goals:list")
    else:
        form = MeilensteinForm()
    return render(request, "goals/meilenstein_form.html", {"form": form, "ziel": ziel})


@login_required
def meilenstein_edit(request, pk):
    meilenstein = get_object_or_404(Meilenstein, pk=pk, jahresziel__user=request.user)
    if request.method == "POST":
        form = MeilensteinForm(request.POST, instance=meilenstein)
        if form.is_valid():
            form.save()
            return redirect("goals:list")
    else:
        form = MeilensteinForm(instance=meilenstein)
    return render(request, "goals/meilenstein_form.html", {"form": form, "ziel": meilenstein.jahresziel})


@login_required
def projekt_add(request, meilenstein_pk):
    meilenstein = get_object_or_404(Meilenstein, pk=meilenstein_pk, jahresziel__user=request.user)
    if request.method == "POST":
        form = ProjektForm(request.POST, instance=Projekt(meilenstein=meilenstein))
        if form.is_valid():
            form.save()
            return redirect("goals:list")
    else:
        form = ProjektForm()
    return render(request, "goals/projekt_form.html", {"form": form, "meilenstein": meilenstein})


@login_required
def projekt_edit(request, pk):
    projekt = get_object_or_404(Projekt, pk=pk, meilenstein__jahresziel__user=request.user)
    if request.method == "POST":
        form = ProjektForm(request.POST, instance=projekt)
        if form.is_valid():
            form.save()
            return redirect("goals:list")
    else:
        form = ProjektForm(instance=projekt)
    return render(request, "goals/projekt_form.html", {"form": form, "meilenstein": projekt.meilenstein})


@require_POST
@login_required
def projekt_toggle_focus(request, pk):
    projekt = get_object_or_404(Projekt, pk=pk, meilenstein__jahresziel__user=request.user)
    iso_year, iso_week, _ = timezone.localdate().isocalendar()
    focus, created = ProjectWeekFocus.objects.get_or_create(projekt=projekt, iso_year=iso_year, iso_week=iso_week)
    if not created:
        focus.delete()
        focused = False
    else:
        focused = True
    return render(request, "goals/_projekt_focus.html", {"projekt": projekt, "focused": focused})


@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user)
    status = request.GET.get("status")
    if status:
        todos = todos.filter(status=status)
    projekt_id = request.GET.get("projekt")
    if projekt_id:
        todos = todos.filter(projekt_id=projekt_id)
    return render(request, "goals/todo_list.html", {"todos": todos, "status": status})


@login_required
def todo_add(request):
    if request.method == "POST":
        form = TodoForm(request.POST, user=request.user)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect("goals:todo-list")
    else:
        form = TodoForm(user=request.user)
    return render(request, "goals/todo_form.html", {"form": form})


@login_required
def todo_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("goals:todo-list")
    else:
        form = TodoForm(instance=todo, user=request.user)
    return render(request, "goals/todo_form.html", {"form": form, "todo": todo})


@require_POST
@login_required
def todo_toggle_done(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if todo.status == Todo.DONE:
        todo.status = Todo.OPEN
        todo.completed_at = None
    else:
        todo.status = Todo.DONE
        todo.completed_at = timezone.now()
    todo.save()
    return render(request, "goals/_todo_row.html", {"todo": todo})


@login_required
def projekt_timeline(request):
    projekte = (
        Projekt.objects.filter(meilenstein__jahresziel__user=request.user)
        .select_related("meilenstein", "meilenstein__jahresziel")
        .order_by("meilenstein__jahresziel_id", "meilenstein_id", "id")
    )
    scheduled = [p for p in projekte if p.start_date and p.end_date]
    unscheduled = [p for p in projekte if not (p.start_date and p.end_date)]

    today = timezone.localdate()
    if scheduled:
        window_start = min(p.start_date for p in scheduled) - timedelta(days=7)
        window_end = max(p.end_date for p in scheduled) + timedelta(days=30)
    else:
        window_start = today - timedelta(days=7)
        window_end = today + timedelta(days=90)
    total_days = max(1, (window_end - window_start).days)

    months = []
    cursor = date(window_start.year, window_start.month, 1)
    while cursor <= window_end:
        offset_days = (cursor - window_start).days
        if offset_days >= 0:
            months.append({"label": cursor.strftime("%b %Y"), "left_px": offset_days * PX_PER_DAY})
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)

    bars = []
    for p in scheduled:
        start_offset = (p.start_date - window_start).days
        duration_days = max(1, (p.end_date - p.start_date).days)
        bars.append(
            {
                "projekt": p,
                "left_px": start_offset * PX_PER_DAY,
                "width_px": duration_days * PX_PER_DAY,
            }
        )

    context = {
        "bars": bars,
        "unscheduled": unscheduled,
        "window_start": window_start,
        "total_days": total_days,
        "timeline_width_px": total_days * PX_PER_DAY,
        "px_per_day": PX_PER_DAY,
        "months": months,
        "today_left_px": (today - window_start).days * PX_PER_DAY,
        "default_duration_days": TIMELINE_DEFAULT_DURATION_DAYS,
    }
    return render(request, "goals/projekt_timeline.html", context)


@require_POST
@login_required
def projekt_update_dates(request, pk):
    projekt = get_object_or_404(Projekt, pk=pk, meilenstein__jahresziel__user=request.user)
    start_raw = request.POST.get("start_date") or None
    end_raw = request.POST.get("end_date") or None
    try:
        new_start = date.fromisoformat(start_raw) if start_raw else None
        new_end = date.fromisoformat(end_raw) if end_raw else None
    except ValueError:
        return JsonResponse({"ok": False, "error": "Ungültiges Datum."}, status=400)

    if new_start and new_end and new_end < new_start:
        return JsonResponse({"ok": False, "error": "Das Bis-Datum muss nach dem Von-Datum liegen."}, status=400)

    projekt.start_date = new_start
    projekt.end_date = new_end
    projekt.save(update_fields=["start_date", "end_date", "updated_at"])
    return JsonResponse(
        {
            "ok": True,
            "id": projekt.id,
            "start_date": new_start.isoformat() if new_start else None,
            "end_date": new_end.isoformat() if new_end else None,
        }
    )
