from django.db import migrations

CATEGORIES = [
    ("beine", "Beine"),
    ("brust", "Brust"),
    ("bizeps", "Bizeps"),
    ("trizeps", "Trizeps"),
    ("ruecken", "Rücken"),
    ("schulter", "Schulter"),
]


def seed_categories(apps, schema_editor):
    ExerciseCategory = apps.get_model("fitness", "ExerciseCategory")
    for code, name in CATEGORIES:
        ExerciseCategory.objects.get_or_create(code=code, defaults={"name": name})


def unseed_categories(apps, schema_editor):
    ExerciseCategory = apps.get_model("fitness", "ExerciseCategory")
    ExerciseCategory.objects.filter(code__in=[code for code, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("fitness", "0001_initial")]
    operations = [migrations.RunPython(seed_categories, unseed_categories)]
