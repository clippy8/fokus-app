from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("onboarding/profil/", views.onboarding_profile, name="onboarding-profile"),
    path("onboarding/ziele/", views.onboarding_goals, name="onboarding-goals"),
]
