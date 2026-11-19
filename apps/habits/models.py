from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

MAX_ACTIVE_HABITS = 5


class Habit(models.Model):
    DAILY = "daily"
    WEEKLY = "weekly"
    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["frequency", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.active:
            qs = Habit.objects.filter(user=self.user, active=True).exclude(pk=self.pk)
            if qs.count() >= MAX_ACTIVE_HABITS:
                raise ValidationError(f"Maximum of {MAX_ACTIVE_HABITS} active habits reached.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DailyHabitCheck(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="daily_checks")
    day = models.ForeignKey("dailydash.Day", on_delete=models.CASCADE, related_name="habit_checks")
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("habit", "day")

    def __str__(self):
        return f"{self.habit.name} / {self.day.date}"


class WeeklyHabitCheck(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="weekly_checks")
    iso_year = models.PositiveSmallIntegerField()
    iso_week = models.PositiveSmallIntegerField()
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("habit", "iso_year", "iso_week")

    def __str__(self):
        return f"{self.habit.name} / {self.iso_year}-W{self.iso_week}"
