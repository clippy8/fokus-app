from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from apps.goals.models import Meilenstein, Projekt

from .forms import DokumentForm, NotizConvertForm, NotizeintragForm
from .models import Dokument, Genre, Notizeintrag


@login_required
def dokument_list(request):
    dokumente = Dokument.objects.filter(user=request.user)

    selected_type = request.GET.get("type", "")
    selected_status = request.GET.get("status", "")
    favorite_only = request.GET.get("favorite") == "1"

    if selected_type:
        dokumente = dokumente.filter(type=selected_type)
    if selected_status:
        dokumente = dokumente.filter(status=selected_status)
    if favorite_only:
        dokumente = dokumente.filter(favorite=True)

    context = {
        "dokumente": dokumente,
        "type_choices": Dokument.TYPE_CHOICES,
        "status_choices": Dokument.STATUS_CHOICES,
        "selected_type": selected_type,
        "selected_status": selected_status,
        "favorite_only": favorite_only,
    }
    return render(request, "dokumente/dokument_list.html", context)


@login_required
def dokument_add(request):
    if request.method == "POST":
        form = DokumentForm(request.POST, request.FILES, instance=Dokument(user=request.user), user=request.user)
        if form.is_valid():
            form.save()
            return redirect("dokumente:list")
    else:
        form = DokumentForm(user=request.user)
    genres = Genre.objects.filter(user=request.user)
    return render(request, "dokumente/dokument_form.html", {"form": form, "genres": genres})


@login_required
def dokument_edit(request, pk):
    dokument = get_object_or_404(Dokument, pk=pk, user=request.user)
    if request.method == "POST":
        form = DokumentForm(request.POST, request.FILES, instance=dokument, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("dokumente:list")
    else:
        form = DokumentForm(instance=dokument, user=request.user)
    genres = Genre.objects.filter(user=request.user)
    context = {
        "form": form,
        "dokument": dokument,
        "genres": genres,
        "notizeintraege": dokument.notizeintraege.all(),
        "notizeintrag_form": NotizeintragForm(),
    }
    return render(request, "dokumente/dokument_form.html", context)


@require_POST
@login_required
def dokument_delete(request, pk):
    dokument = get_object_or_404(Dokument, pk=pk, user=request.user)
    dokument.delete()
    return redirect(request.POST.get("next") or reverse("dokumente:list"))


@require_POST
@login_required
def notizeintrag_add(request, pk):
    dokument = get_object_or_404(Dokument, pk=pk, user=request.user)
    form = NotizeintragForm(request.POST)
    if form.is_valid():
        Notizeintrag.objects.create(dokument=dokument, text=form.cleaned_data["text"])
    return redirect("dokumente:edit", pk=dokument.pk)


@require_POST
@login_required
def notizeintrag_delete(request, pk):
    eintrag = get_object_or_404(Notizeintrag, pk=pk, dokument__user=request.user)
    dokument_pk = eintrag.dokument_id
    eintrag.delete()
    return redirect("dokumente:edit", pk=dokument_pk)


@login_required
def notizeintrag_download(request, pk):
    dokument = get_object_or_404(Dokument, pk=pk, user=request.user)
    bloecke = [
        f"[{eintrag.created_at:%d.%m.%Y %H:%M}]\n{eintrag.text}" for eintrag in dokument.notizeintraege.all()
    ]
    inhalt = "\n\n".join(bloecke) + "\n" if bloecke else ""
    response = HttpResponse(inhalt, content_type="text/plain; charset=utf-8")
    dateiname = slugify(dokument.title) or "notizen"
    response["Content-Disposition"] = f'attachment; filename="{dateiname}-notizen.txt"'
    return response


@login_required
def notiz_convert(request, pk):
    dokument = get_object_or_404(Dokument, pk=pk, user=request.user, type=Dokument.NOTIZ)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("dokumente:list")

    if not Meilenstein.objects.filter(jahresziel__user=request.user, jahresziel__archived=False).exists():
        messages.error(
            request,
            "Lege zuerst ein Jahresziel mit Meilenstein an, bevor du eine Notiz in ein Projekt umwandelst.",
        )
        return redirect(next_url)

    if request.method == "POST":
        form = NotizConvertForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            Projekt.objects.create(
                meilenstein=cd["meilenstein"],
                title=cd["title"],
                description=cd["description"],
                next_step=cd["next_step"],
            )
            dokument.delete()
            return redirect(request.POST.get("next") or reverse("goals:projekt-timeline"))
    else:
        form = NotizConvertForm(
            user=request.user, initial={"title": dokument.title, "description": dokument.comment}
        )
    return render(
        request,
        "dokumente/notiz_convert.html",
        {"form": form, "dokument": dokument, "next": next_url},
    )
