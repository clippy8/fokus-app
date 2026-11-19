from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import redirect, render

from apps.goals.forms import OnboardingGoalForm
from apps.goals.models import Jahresziel

from .forms import OnboardingProfileForm, RegisterForm

# Onboarding is a short, ordered chain of setup steps shown once right after
# registration. Each step's view redirects to the next step's name here; the
# last step redirects to the dashboard. Add new steps by inserting another
# "stepN" view below and pointing the previous step's redirect at it.
NEXT_AFTER_ONBOARDING_PROFILE = "accounts:onboarding-goals"
NEXT_AFTER_ONBOARDING_GOALS = "dailydash:today"

JahreszielFormSet = formset_factory(
    OnboardingGoalForm, extra=3, min_num=3, max_num=3, validate_min=True, validate_max=True
)


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
    return render(request, "accounts/onboarding_goals.html", {"formset": formset})
