from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import redirect, render

from apps.goals.forms import OnboardingGoalForm, OnboardingMeilensteinForm
from apps.goals.models import Jahresziel

from .forms import OnboardingProfileForm, RegisterForm

# Onboarding is a short, ordered chain of setup steps shown once right after
# registration. Each step's view redirects to the next step's name here; the
# last step redirects to the dashboard. Add new steps by inserting another
# "stepN" view below and pointing the previous step's redirect at it.
NEXT_AFTER_ONBOARDING_PROFILE = "accounts:onboarding-goals"
NEXT_AFTER_ONBOARDING_GOALS = "accounts:onboarding-meilensteine"
NEXT_AFTER_ONBOARDING_MEILENSTEINE = "dailydash:today"

JahreszielFormSet = formset_factory(
    OnboardingGoalForm, extra=3, min_num=3, max_num=3, validate_min=True, validate_max=True
)

MeilensteinFormSet = formset_factory(
    OnboardingMeilensteinForm, extra=3, min_num=3, max_num=3, validate_min=True, validate_max=True
)

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
