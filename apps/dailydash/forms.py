from django import forms

from .models import RoutineItem


class RoutineItemForm(forms.ModelForm):
    class Meta:
        model = RoutineItem
        fields = ["name", "timing", "order"]


class OnboardingRoutineItemForm(forms.ModelForm):
    class Meta:
        model = RoutineItem
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Punkt der Routine"}),
        }
