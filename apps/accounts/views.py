from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, modelformset_factory
from django.shortcuts import redirect, render

from apps.dailydash.forms import OnboardingRoutineItemForm
from apps.dailydash.models import RoutineItem
from apps.goals.forms import OnboardingGoalForm, OnboardingMeilensteinForm, OnboardingProjektIdeaForm
from apps.goals.models import Jahresziel, Meilenstein, Projekt

from .forms import OnboardingProfileForm, RegisterForm

# Onboarding is a short, ordered chain of setup steps shown once right after
# registration. Each step's view redirects to the next step's name here; the
# last step redirects to the dashboard. Add new steps by inserting another
# "stepN" view below and pointing the previous step's redirect at it.
NEXT_AFTER_ONBOARDING_PROFILE = "accounts:onboarding-goals"
NEXT_AFTER_ONBOARDING_GOALS = "accounts:onboarding-meilensteine"
NEXT_AFTER_ONBOARDING_MEILENSTEINE = "accounts:onboarding-projekte"
NEXT_AFTER_ONBOARDING_PROJEKTE = "accounts:onboarding-routinen"
NEXT_AFTER_ONBOARDING_ROUTINEN = "dailydash:today"

JahreszielFormSet = formset_factory(
    OnboardingGoalForm, extra=3, min_num=3, max_num=3, validate_min=True, validate_max=True
)

MeilensteinFormSet = formset_factory(
    OnboardingMeilensteinForm, extra=3, min_num=3, max_num=3, validate_min=True, validate_max=True
)

# Projekt ideas are an open-ended brainstorm, not a fixed count: no min/max,
# and a modelformset (not a plain formset) so revisiting this step shows
# ideas already captured and lets you add more or discard ones you typed.
ProjektIdeaFormSet = modelformset_factory(Projekt, form=OnboardingProjektIdeaForm, extra=1, can_delete=True)

# Routine items: open-ended like project ideas. On a first visit we seed each
# list with example rows (editable/removable, not yet saved); on a revisit the
# existing items show instead and one blank extra row is offered for more.
RoutineItemSeedFormSet = modelformset_factory(
    RoutineItem, form=OnboardingRoutineItemForm, extra=4, can_delete=True
)
RoutineItemFormSet = modelformset_factory(RoutineItem, form=OnboardingRoutineItemForm, extra=1, can_delete=True)

MORNING_ROUTINE_EXAMPLES = ["Wasser trinken", "Liegestütze", "Kalender checken", "Bett machen"]
EVENING_ROUTINE_EXAMPLES = [
    "Zimmer aufräumen",
    "Daily-Todos erledigen",
    "Instagram & WhatsApp checken",
    "Planung: Nächsten Tag im Kalender planen",
]

GOAL_TITLE_EXAMPLES = ["Sportlich werden", "Einkommen verdoppeln", "Eigene App veröffentlichen"]


def _apply_example_placeholders(formset):
    for form, example in zip(formset.forms, GOAL_TITLE_EXAMPLES):
        form.fields["title"].widget.attrs["placeholder"] = f"Titel, z. B. „{example}“"


def register(request):
    if request.user.is_authenticated:
        return redirect("dailydash:today")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:onboarding-profile")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def onboarding_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        if "skip" not in request.POST:
            form = OnboardingProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return redirect(NEXT_AFTER_ONBOARDING_PROFILE)
        else:
            return redirect(NEXT_AFTER_ONBOARDING_PROFILE)
    else:
        form = OnboardingProfileForm(instance=profile)
    return render(request, "accounts/onboarding_profile.html", {"form": form})


@login_required
def onboarding_goals(request):
    if Jahresziel.objects.filter(user=request.user, archived=False).count() >= 3:
        return redirect(NEXT_AFTER_ONBOARDING_GOALS)

    if request.method == "POST":
        formset = JahreszielFormSet(request.POST, prefix="goal")
        for form in formset.forms:
            form.instance.user = request.user
        if formset.is_valid():
            for form in formset:
                ziel = form.save(commit=False)
                ziel.current_value = ziel.start_value
                ziel.save()
            return redirect(NEXT_AFTER_ONBOARDING_GOALS)
    else:
        formset = JahreszielFormSet(prefix="goal")
    _apply_example_placeholders(formset)
    return render(request, "accounts/onboarding_goals.html", {"formset": formset})


@login_required
def onboarding_meilensteine(request):
    jahresziele = list(Jahresziel.objects.filter(user=request.user, archived=False).order_by("id"))
    if not jahresziele or all(ziel.meilensteine.count() >= 3 for ziel in jahresziele):
        return redirect(NEXT_AFTER_ONBOARDING_MEILENSTEINE)

    if request.method == "POST":
        formsets = {ziel.id: MeilensteinFormSet(request.POST, prefix=f"ziel{ziel.id}") for ziel in jahresziele}
        for ziel in jahresziele:
            for form in formsets[ziel.id].forms:
                form.instance.jahresziel = ziel
        if all(formsets[ziel.id].is_valid() for ziel in jahresziele):
            for ziel in jahresziele:
                for form in formsets[ziel.id]:
                    meilenstein = form.save(commit=False)
                    meilenstein.current_value = meilenstein.start_value
                    meilenstein.save()
            return redirect(NEXT_AFTER_ONBOARDING_MEILENSTEINE)
    else:
        formsets = {ziel.id: MeilensteinFormSet(prefix=f"ziel{ziel.id}") for ziel in jahresziele}

    sections = []
    for ziel in jahresziele:
        formset = formsets[ziel.id]
        for form in formset.forms:
            form.fields["title"].widget.attrs["placeholder"] = "Name des Meilensteins"
        sections.append({"ziel": ziel, "formset": formset})
    return render(request, "accounts/onboarding_meilensteine.html", {"sections": sections})


@login_required
def onboarding_projekte(request):
    meilensteine = list(
        Meilenstein.objects.filter(jahresziel__user=request.user, jahresziel__archived=False)
        .select_related("jahresziel")
        .order_by("jahresziel_id", "id")
    )
    if not meilensteine:
        return redirect(NEXT_AFTER_ONBOARDING_PROJEKTE)

    if request.method == "POST":
        formsets = {
            m.id: ProjektIdeaFormSet(
                request.POST, prefix=f"m{m.id}", queryset=Projekt.objects.filter(meilenstein=m)
            )
            for m in meilensteine
        }
        if all(formsets[m.id].is_valid() for m in meilensteine):
            for m in meilensteine:
                formset = formsets[m.id]
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for instance in instances:
                    instance.meilenstein = m
                    instance.save()
            return redirect(NEXT_AFTER_ONBOARDING_PROJEKTE)
    else:
        formsets = {
            m.id: ProjektIdeaFormSet(prefix=f"m{m.id}", queryset=Projekt.objects.filter(meilenstein=m))
            for m in meilensteine
        }

    ziele_order = []
    sections_by_ziel = {}
    for m in meilensteine:
        ziel = m.jahresziel
        if ziel.id not in sections_by_ziel:
            ziele_order.append(ziel)
            sections_by_ziel[ziel.id] = {"ziel": ziel, "items": []}
        sections_by_ziel[ziel.id]["items"].append({"meilenstein": m, "formset": formsets[m.id]})
    sections = [sections_by_ziel[ziel.id] for ziel in ziele_order]
    return render(request, "accounts/onboarding_projekte.html", {"sections": sections})


def _routine_formset_for_get(user, timing, examples, prefix):
    queryset = RoutineItem.objects.filter(user=user, timing=timing)
    if queryset.exists():
        return RoutineItemFormSet(prefix=prefix, queryset=queryset)
    return RoutineItemSeedFormSet(prefix=prefix, queryset=queryset, initial=[{"name": n} for n in examples])


@login_required
def onboarding_routinen(request):
    if request.method == "POST":
        morning_formset = RoutineItemFormSet(
            request.POST,
            prefix="morning",
            queryset=RoutineItem.objects.filter(user=request.user, timing=RoutineItem.MORNING),
        )
        evening_formset = RoutineItemFormSet(
            request.POST,
            prefix="evening",
            queryset=RoutineItem.objects.filter(user=request.user, timing=RoutineItem.EVENING),
        )
        if morning_formset.is_valid() and evening_formset.is_valid():
            for formset, timing in (
                (morning_formset, RoutineItem.MORNING),
                (evening_formset, RoutineItem.EVENING),
            ):
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for instance in instances:
                    instance.user = request.user
                    instance.timing = timing
                    instance.save()
            return redirect(NEXT_AFTER_ONBOARDING_ROUTINEN)
    else:
        morning_formset = _routine_formset_for_get(
            request.user, RoutineItem.MORNING, MORNING_ROUTINE_EXAMPLES, "morning"
        )
        evening_formset = _routine_formset_for_get(
            request.user, RoutineItem.EVENING, EVENING_ROUTINE_EXAMPLES, "evening"
        )

    context = {"morning_formset": morning_formset, "evening_formset": evening_formset}
    return render(request, "accounts/onboarding_routinen.html", context)
