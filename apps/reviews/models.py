from django.conf import settings
from django.db import models


class WeeklyReview(models.Model):
    YES = "yes"
    NO = "no"
    PARTIAL = "partial"
    ACHIEVED_CHOICES = [
        (YES, "Ja"),
        (NO, "Nein"),
        (PARTIAL, "Teilweise"),
    ]

    DRAFT = "draft"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (DRAFT, "Entwurf"),
        (COMPLETED, "Abgeschlossen"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weekly_reviews")
    iso_year = models.PositiveSmallIntegerField()
    iso_week = models.PositiveSmallIntegerField()

    reflection_good = models.TextField(blank=True)
    reflection_improve = models.TextField(blank=True)

    weekly_goal_text = models.TextField(blank=True)
    weekly_goal_achieved = models.CharField(max_length=10, choices=ACHIEVED_CHOICES, blank=True)
    weekly_goal_reflection = models.TextField(blank=True)

    numbers_reviewed = models.BooleanField(default=False)
    most_important_confirmed = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "iso_year", "iso_week")
        ordering = ["-iso_year", "-iso_week"]

    def __str__(self):
        return f"{self.user.username} — {self.iso_year}-W{self.iso_week}"
