from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    geburtstag = models.DateField(null=True, blank=True)
    groesse_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    gewicht_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kalorienziel_kcal = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
