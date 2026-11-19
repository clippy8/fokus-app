from django.conf import settings
from django.db import models


class RoutineItem(models.Model):
    MORNING = "morning"
    EVENING = "evening"
    TIMING_CHOICES = [
        (MORNING, "Morgenroutine"),
        (EVENING, "Abendroutine"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="routine_items")
    name = models.CharField(max_length=200)
    timing = models.CharField(max_length=10, choices=TIMING_CHOICES)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timing", "order", "id"]

    def __str__(self):
        return f"{self.get_timing_display()}: {self.name}"


class Day(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    journal_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} — {self.date}"


class DayRoutineCheck(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="routine_checks")
    routine_item = models.ForeignKey(RoutineItem, on_delete=models.CASCADE, related_name="day_checks")
    checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("day", "routine_item")
        ordering = ["routine_item__timing", "routine_item__order"]

    def __str__(self):
        return f"{self.day} / {self.routine_item.name}"
