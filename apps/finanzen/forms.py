from django import forms

from .models import FinanceEntry

# HTML5 <input type="datetime-local"> requires the value attribute in ISO format
# (YYYY-MM-DDTHH:MM) regardless of UI locale. Without an explicit format, Django renders
# the value in the active locale's format when pre-filling an existing instance, which the
# browser then can't parse — the field silently shows up empty.
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


class FinanceEntryForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format=ISO_DATETIME_FORMAT),
        input_formats=[ISO_DATETIME_FORMAT],
    )

    class Meta:
        model = FinanceEntry
        fields = ["name", "tag", "amount", "timestamp", "category"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "z. B. Netflix"}),
            "tag": forms.TextInput(attrs={"placeholder": "z. B. Unterhaltung"}),
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
        }
