from django.conf import settings
from django.db import models


class FinanceEntry(models.Model):
    FIXKOSTEN = "fixkosten"
    AUSGABEN = "ausgaben"
    EINNAHMEN = "einnahmen"
    CATEGORY_CHOICES = [
        (FIXKOSTEN, "Fixkosten"),
        (AUSGABEN, "Ausgaben"),
        (EINNAHMEN, "Einnahmen"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_entries")
    name = models.CharField(max_length=200, verbose_name="Name der Ausgabe")
    tag = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Höhe (€)")
    timestamp = models.DateTimeField(verbose_name="Zeit")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.name} ({self.amount} €)"
