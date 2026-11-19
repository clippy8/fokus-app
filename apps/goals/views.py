from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import JahreszielForm, MeilensteinForm, ProjektForm, TodoForm
from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt, Todo


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
