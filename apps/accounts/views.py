from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import OnboardingProfileForm, RegisterForm

# Onboarding is a short, ordered chain of optional setup steps shown once right
# after registration. Each step's view redirects to the next step's name here;
# the last step redirects to the dashboard. Add new steps by inserting another
# "stepN" view below and pointing the previous step's redirect at it.
NEXT_AFTER_ONBOARDING_PROFILE = "dailydash:today"


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
