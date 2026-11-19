from django.conf import settings
from django.db import models


class ExerciseCategory(models.Model):
    BEINE = "beine"
    BRUST = "brust"
    BIZEPS = "bizeps"
    TRIZEPS = "trizeps"
    RUECKEN = "ruecken"
    SCHULTER = "schulter"
    CODE_CHOICES = [
        (BEINE, "Beine"),
        (BRUST, "Brust"),
        (BIZEPS, "Bizeps"),
        (TRIZEPS, "Trizeps"),
        (RUECKEN, "Rücken"),
        (SCHULTER, "Schulter"),
    ]

    code = models.CharField(max_length=10, choices=CODE_CHOICES, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "exercise categories"

    def __str__(self):
        return self.name


class Exercise(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=200)
    equipment_number = models.CharField(max_length=50, blank=True, verbose_name="Gerätenummer")
    equipment_setting = models.CharField(max_length=200, blank=True, verbose_name="Geräteeinstellung")
    image = models.ImageField(upload_to="fitness/exercises/", null=True, blank=True, verbose_name="Bild/GIF")
    categories = models.ManyToManyField(ExerciseCategory, related_name="exercises", blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkoutSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="sets")
    day = models.ForeignKey("dailydash.Day", on_delete=models.CASCADE, related_name="workout_sets")
    set_number = models.PositiveSmallIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-day__date", "exercise__name", "set_number"]
        unique_together = ("user", "exercise", "day", "set_number")

    def __str__(self):
        return f"{self.exercise.name} / {self.day.date} / Satz {self.set_number}"


class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="fitness/recipes/", null=True, blank=True)
    calories_kcal_per_100g = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Kalorien pro 100 g (kcal)"
    )
    protein_g_per_100g = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True, verbose_name="Protein pro 100 g (g)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodLogEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_log_entries")
    day = models.ForeignKey("dailydash.Day", on_delete=models.CASCADE, related_name="food_log_entries")
    name = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name="log_entries")
    amount_g = models.PositiveIntegerField(null=True, blank=True, verbose_name="Menge (g)")
    calories_kcal = models.PositiveIntegerField(null=True, blank=True)
    protein_g = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-day__date", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.day.date})"
