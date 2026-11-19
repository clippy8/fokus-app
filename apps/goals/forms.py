from django import forms

from .models import Jahresziel, Meilenstein, Projekt, Todo


# HTML5 <input type="date"> requires the value attribute in ISO format (YYYY-MM-DD)
# regardless of UI locale. Without an explicit format, Django renders the value in the
# active locale's date format (e.g. German DD.MM.YYYY) when pre-filling an existing
# instance, which the browser then can't parse — the field silently shows up empty.
ISO_DATE_FORMAT = "%Y-%m-%d"

DATE_WIDGETS = {
    "start_date": forms.DateInput(attrs={"type": "date"}, format=ISO_DATE_FORMAT),
    "end_date": forms.DateInput(attrs={"type": "date"}, format=ISO_DATE_FORMAT),
}


def title_input_widget(placeholder, aria_label):
    return forms.TextInput(
        attrs={"class": "goal-title-input", "placeholder": placeholder, "aria-label": aria_label}
    )


class JahreszielForm(forms.ModelForm):
    class Meta:
        model = Jahresziel
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
            "start_value",
            "target_value",
            "current_value",
            "status",
        ]
        widgets = {
            **DATE_WIDGETS,
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OnboardingGoalForm(forms.ModelForm):
    class Meta:
        model = Jahresziel
        fields = ["title", "description", "start_date", "end_date", "start_value", "target_value"]
        widgets = {
            "title": title_input_widget("Titel, z. B. „Sportlich werden“", "Titel des Ziels"),
            **DATE_WIDGETS,
            "description": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "start_value": "Start",
            "target_value": "Ziel",
        }


class MeilensteinForm(forms.ModelForm):
    class Meta:
        model = Meilenstein
        fields = [
            "title",
            "description",
            "deadline",
            "start_value",
            "target_value",
            "current_value",
            "status",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}, format=ISO_DATE_FORMAT),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OnboardingMeilensteinForm(forms.ModelForm):
    class Meta:
        model = Meilenstein
        fields = ["title", "description", "deadline", "start_value", "target_value"]
        widgets = {
            "title": title_input_widget("Name des Meilensteins", "Name des Meilensteins"),
            "deadline": forms.DateInput(attrs={"type": "date"}, format=ISO_DATE_FORMAT),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "start_value": "Start",
            "target_value": "Ziel",
        }


class ProjektForm(forms.ModelForm):
    class Meta:
        model = Projekt
        fields = ["title", "description", "next_step", "start_date", "end_date", "status"]
        widgets = {
            **DATE_WIDGETS,
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OnboardingProjektIdeaForm(forms.ModelForm):
    class Meta:
        model = Projekt
        fields = ["title", "next_step", "start_date", "end_date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Projektidee"}),
            "next_step": forms.TextInput(attrs={"placeholder": "Nächster Schritt (optional)"}),
            **DATE_WIDGETS,
        }
        labels = {
            "start_date": "Von",
            "end_date": "Bis",
        }


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["title", "description", "due_date", "projekt"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["projekt"].queryset = Projekt.objects.filter(meilenstein__jahresziel__user=user)
