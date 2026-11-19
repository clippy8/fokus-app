from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

MAX_JAHRESZIELE = 3
MAX_MEILENSTEINE_PER_ZIEL = 3


class Jahresziel(models.Model):
    ON_TRACK = "on_track"
    OFF_TRACK = "off_track"
    AT_RISK = "at_risk"
    ACHIEVED = "achieved"
    STATUS_CHOICES = [
        (ON_TRACK, "On Track"),
        (OFF_TRACK, "Off Track"),
        (AT_RISK, "At Risk"),
        (ACHIEVED, "Achieved"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jahresziele")
    title = models.CharField(max_length=255)
    description = models.TextField(
        verbose_name="Beschreibung",
        help_text=(
            "Mach den Titel konkret: Woran erkennst du eindeutig, dass du das Ziel erreicht hast? "
            "Beispiel bei Titel „Sportlich werden“: „100 Liegestütze am Stück schaffen“ oder "
            "„Ein Sixpack bekommen“."
        )
    )
    start_date = models.DateField(verbose_name="Von")
    end_date = models.DateField(verbose_name="Bis")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ON_TRACK)
    archived = models.BooleanField(default=False)
    start_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Start")
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Stand")
    target_value = models.DecimalField(max_digits=12, decimal_places=2, default=1, verbose_name="Ziel")
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["end_date", "order", "id"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "Das Enddatum muss nach dem Startdatum liegen."})
        if not self.archived:
            qs = Jahresziel.objects.filter(user=self.user, archived=False).exclude(pk=self.pk)
            if qs.count() >= MAX_JAHRESZIELE:
                raise ValidationError(f"Maximum of {MAX_JAHRESZIELE} active Jahresziele reached.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def progress_percent(self):
        span = self.target_value - self.start_value
        if span == 0:
            return 100 if self.status == self.ACHIEVED else 0
        raw = (self.current_value - self.start_value) / span * 100
        return max(0, min(100, round(raw)))

    @property
    def time_percent(self):
        total_days = (self.end_date - self.start_date).days
        if total_days <= 0:
            return 100
        elapsed_days = (timezone.localdate() - self.start_date).days
        return max(0, min(100, round(elapsed_days / total_days * 100)))


class Meilenstein(models.Model):
    ON_TRACK = "on_track"
    OFF_TRACK = "off_track"
    NOT_STARTED = "not_started"
    AT_RISK = "at_risk"
    STATUS_CHOICES = [
        (ON_TRACK, "On Track"),
        (OFF_TRACK, "Off Track"),
        (NOT_STARTED, "Not Started"),
        (AT_RISK, "At Risk"),
    ]

    jahresziel = models.ForeignKey(Jahresziel, on_delete=models.CASCADE, related_name="meilensteine")
    title = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(
        verbose_name="Beschreibung",
        help_text=(
            "Beschreibe, woran du eindeutig erkennst, dass dieser Meilenstein erreicht ist und das "
            "Jahresziel dadurch ein großes Stück näher gerückt ist."
        ),
    )
    deadline = models.DateField(verbose_name="Deadline")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NOT_STARTED)
    start_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Start")
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Stand")
    target_value = models.DecimalField(max_digits=12, decimal_places=2, default=1, verbose_name="Ziel")
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["deadline", "order", "id"]

    def __str__(self):
        return self.title

    def clean(self):
        qs = Meilenstein.objects.filter(jahresziel=self.jahresziel).exclude(pk=self.pk)
        if qs.count() >= MAX_MEILENSTEINE_PER_ZIEL:
            raise ValidationError(f"Maximum of {MAX_MEILENSTEINE_PER_ZIEL} Meilensteine per Jahresziel reached.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def progress_percent(self):
        span = self.target_value - self.start_value
        if span == 0:
            return 100 if self.current_value >= self.target_value else 0
        raw = (self.current_value - self.start_value) / span * 100
        return max(0, min(100, round(raw)))


class Projekt(models.Model):
    NOT_STARTED = "not_started"
    ON_HOLD = "on_hold"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    STATUS_CHOICES = [
        (NOT_STARTED, "Nicht begonnen"),
        (ON_HOLD, "Pausiert"),
        (ACTIVE, "Aktiv"),
        (COMPLETED, "Abgeschlossen"),
        (ABANDONED, "Verworfen"),
    ]

    meilenstein = models.ForeignKey(Meilenstein, on_delete=models.CASCADE, related_name="projekte")
    title = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        verbose_name="Beschreibung",
        help_text="Welche einzelnen Schritte sind für dieses Projekt nötig?",
    )
    next_step = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nächste Aktion",
        help_text=(
            "Ein ganz kleinschrittiges nächstes To-do, z. B. „Trainingsplan-Vorlage googeln“ statt "
            "„Trainingsplan erstellen“."
        ),
    )
    start_date = models.DateField(null=True, blank=True, verbose_name="Von")
    end_date = models.DateField(null=True, blank=True, verbose_name="Bis")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NOT_STARTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["end_date", "id"]

    def __str__(self):
        return self.title

    def is_focused_in(self, iso_year, iso_week):
        return self.week_focus_entries.filter(iso_year=iso_year, iso_week=iso_week).exists()


class ProjectWeekFocus(models.Model):
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, related_name="week_focus_entries")
    iso_year = models.PositiveSmallIntegerField()
    iso_week = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("projekt", "iso_year", "iso_week")

    def __str__(self):
        return f"{self.projekt.title} / {self.iso_year}-W{self.iso_week}"


class Todo(models.Model):
    OPEN = "open"
    DONE = "done"
    STATUS_CHOICES = [
        (OPEN, "Open"),
        (DONE, "Done"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    projekt = models.ForeignKey(Projekt, null=True, blank=True, on_delete=models.SET_NULL, related_name="todos")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return self.title
