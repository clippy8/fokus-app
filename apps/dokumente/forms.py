from django import forms

from apps.goals.models import Meilenstein

from .models import Dokument, Genre, Notizeintrag


class DokumentForm(forms.ModelForm):
    genre = forms.CharField(
        max_length=100,
        required=False,
        label="Genre",
        widget=forms.TextInput(
            attrs={"list": "genre-options", "autocomplete": "off", "placeholder": "z. B. Fantasy"}
        ),
    )
    field_order = ["type", "title", "genre", "status", "favorite", "rating", "comment", "url", "image"]

    class Meta:
        model = Dokument
        fields = ["type", "title", "status", "favorite", "rating", "comment", "url", "image"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Neues Dokument",
                    "autofocus": True,
                    "style": (
                        "font-size: 1.75rem; font-weight: 700; border: none; padding: 0; "
                        "margin-bottom: 1rem; background: transparent; width: 100%;"
                    ),
                }
            ),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 4}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.genre_id:
            self.fields["genre"].initial = self.instance.genre.name

    def save(self, commit=True):
        dokument = super().save(commit=False)
        dokument.genre = Genre.get_or_create_by_name(self.user, self.cleaned_data.get("genre"))
        if commit:
            dokument.save()
        return dokument


class NotizeintragForm(forms.ModelForm):
    class Meta:
        model = Notizeintrag
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Neue Notiz..."}),
        }
        labels = {"text": ""}


class NotizConvertForm(forms.Form):
    meilenstein = forms.ModelChoiceField(queryset=Meilenstein.objects.none(), label="Meilenstein")
    title = forms.CharField(max_length=255, label="Titel")
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Beschreibung", required=False)
    next_step = forms.CharField(max_length=255, label="Nächste Aktion", required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meilenstein"].queryset = Meilenstein.objects.filter(
            jahresziel__user=user, jahresziel__archived=False
        )
