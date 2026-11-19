from django import forms
from django.forms import modelformset_factory

from .models import Exercise, FoodLogEntry, Recipe, WorkoutSet


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "equipment_number", "equipment_setting", "image", "categories"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "goal-title-input", "placeholder": "Name der Übung"}),
            "categories": forms.CheckboxSelectMultiple,
        }


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "text", "image", "calories_kcal_per_100g", "protein_g_per_100g"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 6}),
        }


class FoodLogEntryForm(forms.ModelForm):
    class Meta:
        model = FoodLogEntry
        fields = ["name", "recipe", "amount_g", "calories_kcal", "protein_g"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["recipe"].queryset = Recipe.objects.filter(user=user)


class WorkoutSetEntryForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = ["reps", "weight_kg"]


WorkoutSetFormSet = modelformset_factory(WorkoutSet, form=WorkoutSetEntryForm, extra=1, can_delete=True)
