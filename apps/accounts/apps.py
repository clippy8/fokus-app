from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    label = 'accounts'

    def ready(self):
        from . import signals  # noqa: F401

        # Django 6.1's new default blank-choice label ("- Select an option -") isn't yet
        # translated in Django's own German locale catalog. Override it project-wide here,
        # the extension point Django's own source comment calls out for exactly this.
        from django.db.models import fields as model_fields

        model_fields.BLANK_CHOICE_LABEL = "Bitte auswählen"
