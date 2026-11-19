from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("onboarding/profil/", views.onboarding_profile, name="onboarding-profile"),
    path("onboarding/ziele/", views.onboarding_goals, name="onboarding-goals"),
    path("onboarding/meilensteine/", views.onboarding_meilensteine, name="onboarding-meilensteine"),
    path("onboarding/projekte/", views.onboarding_projekte, name="onboarding-projekte"),
    path("onboarding/routinen/", views.onboarding_routinen, name="onboarding-routinen"),
]
