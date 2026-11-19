from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = User._meta.get_field("first_name").formfield(required=False)
    last_name = User._meta.get_field("last_name").formfield(required=False)
    email = User._meta.get_field("email").formfield(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class OnboardingProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["groesse_cm", "gewicht_kg"]
        labels = {
            "groesse_cm": "Größe (cm)",
            "gewicht_kg": "Gewicht (kg)",
        }
