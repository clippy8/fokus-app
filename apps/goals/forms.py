from django import forms

from .models import Jahresziel, Meilenstein, Projekt, Todo


class JahreszielForm(forms.ModelForm):
    class Meta:
        model = Jahresziel
        fields = ["title", "description", "year"]


class MeilensteinForm(forms.ModelForm):
    class Meta:
        model = Meilenstein
        fields = ["title", "target_date"]


class ProjektForm(forms.ModelForm):
    class Meta:
        model = Projekt
        fields = ["title", "description", "end_date", "status"]


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["title", "description", "due_date", "projekt"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["projekt"].queryset = Projekt.objects.filter(meilenstein__jahresziel__user=user)
