from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Genre(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="genres")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_by_name(cls, user, name):
        name = (name or "").strip()
        if not name:
            return None
        existing = cls.objects.filter(user=user, name__iexact=name).first()
        if existing:
            return existing
        return cls.objects.create(user=user, name=name)


class Dokument(models.Model):
    BUCH = "buch"
    FILM = "film"
    REZEPT = "rezept"
    NOTIZ = "notiz"
    PODCAST = "podcast"
    ARTIKEL = "artikel"
    COMPUTERSPIEL = "computerspiel"
    TYPE_CHOICES = [
        (BUCH, "Buch"),
        (FILM, "Film"),
        (REZEPT, "Rezept"),
        (NOTIZ, "Notiz"),
        (PODCAST, "Podcast"),
        (ARTIKEL, "Artikel"),
        (COMPUTERSPIEL, "Computerspiel"),
    ]

    GEPLANT = "geplant"
    KONSUMIEREND = "konsumierend"
    KONSUMIERT = "konsumiert"
    STATUS_CHOICES = [
        (GEPLANT, "Geplant"),
        (KONSUMIEREND, "Aktiv"),
        (KONSUMIERT, "Abgeschlossen"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dokumente")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Typ")
    title = models.CharField(max_length=255, verbose_name="Titel")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name="dokumente")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=GEPLANT)
    favorite = models.BooleanField(default=False, verbose_name="Favorit")
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Bewertung"
    )
    comment = models.TextField(blank=True, verbose_name="Kommentar")
    url = models.URLField(blank=True, verbose_name="URL")
    image = models.ImageField(upload_to="dokumente/", null=True, blank=True, verbose_name="Bild")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    @property
    def rating_stars(self):
        return "★" * self.rating if self.rating else ""


class Notizeintrag(models.Model):
    dokument = models.ForeignKey(Dokument, on_delete=models.CASCADE, related_name="notizeintraege")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.dokument.title} — {self.created_at:%d.%m.%Y %H:%M}"
