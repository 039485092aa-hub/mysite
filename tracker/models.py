from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models


# Treenityypit (koodit A–G kuten kuvauksessasi)
WORKOUT_CHOICES = [
    ("A", "Punttisali, ohjelma 1"),
    ("B", "Punttisali, ohjelma 2"),
    ("C", "Juoksu, pitkä"),
    ("D", "Juoksu, intervalli"),
    ("E", "Kävely, pitkä"),
    ("F", "Kävely, palauttava/kevyt"),
    ("G", "Lepopäivä"),
]

WEEKDAY_CHOICES = [
    (0, "Ma"),
    (1, "Ti"),
    (2, "Ke"),
    (3, "To"),
    (4, "Pe"),
    (5, "La"),
    (6, "Su"),
]


def ddmm(d) -> str:
    """Esitysmuoto pp.kk. (ilman vuotta)."""
    if not d:
        return ""
    return d.strftime("%d.%m.")


class WeekPlan(models.Model):
    """
    Viikkokohtainen suunnitelma. Viikon aloituspäivä on aina maanantai.
    """
    week_start_date = models.DateField(
        unique=True,
        help_text="Viikon aloituspäivä (maanantai).",
        verbose_name="Viikon aloituspäivä",
    )
    title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Vapaaehtoinen otsikko viikolle.",
        verbose_name="Otsikko",
    )

    class Meta:
        ordering = ["-week_start_date"]
        verbose_name = "Viikkosuunnitelma"
        verbose_name_plural = "Viikkosuunnitelmat"

    def clean(self):
        # Python: Monday = 0 ... Sunday = 6
        if self.week_start_date and self.week_start_date.weekday() != 0:
            raise ValidationError({"week_start_date": "Viikon aloituspäivän täytyy olla maanantai."})

    @property
    def week_end_date(self):
        return self.week_start_date + timedelta(days=6)

    def __str__(self):
        # Näytetään päivämäärät pp.kk. – pp.kk.
        start = ddmm(self.week_start_date)
        end = ddmm(self.week_end_date)
        extra = f" — {self.title}" if self.title else ""
        return f"Viikko {start}–{end}{extra}"


class PlanDay(models.Model):
    """
    Yksi viikonpäivä viikkosuunnitelmassa.
    Yksi päivä voi sisältää vain yhden treenivalinnan (toteutetaan unique-rajoitteella).
    """
    week_plan = models.ForeignKey(WeekPlan, on_delete=models.CASCADE, related_name="days")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES, verbose_name="Viikonpäivä")
    planned_workout = models.CharField(max_length=1, choices=WORKOUT_CHOICES, verbose_name="Suunniteltu treeni")

    class Meta:
        ordering = ["week_plan__week_start_date", "weekday"]
        verbose_name = "Suunnitelmapäivä"
        verbose_name_plural = "Suunnitelmapäivät"
        constraints = [
            models.UniqueConstraint(fields=["week_plan", "weekday"], name="unique_plan_day_per_week"),
        ]

    @property
    def date(self):
        """Päivämäärä kyseiselle viikonpäivälle (pp.kk. näkyviin adminissa)."""
        return self.week_plan.week_start_date + timedelta(days=int(self.weekday))

    def __str__(self):
        return f"{self.get_weekday_display()} {ddmm(self.date)} — {self.get_planned_workout_display()}"


class WorkoutLog(models.Model):
    """
    Toteuma-/tapahtumaloki päivälle:
    - completed = Kyllä/Ei (toteutuiko)
    - voi olla myös ilman suunnitelmaa (planned_day on optional)
    - yksi toteuma per päivämäärä (yksi päivä sisältää yhden treenin)
    """
    date = models.DateField(unique=True, verbose_name="Päivämäärä")
    workout = models.CharField(max_length=1, choices=WORKOUT_CHOICES, verbose_name="Treeni")
    completed = models.BooleanField(default=False, help_text="Toteutuiko treeni? (Kyllä/Ei)", verbose_name="Toteutui")
    planned_day = models.ForeignKey(
        PlanDay,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
        help_text="Valinnainen linkki suunnitelmapäivään (voi olla tyhjä, jos toteuma ei ollut suunnitelmassa).",
        verbose_name="Suunnitelmapäivä",
    )
    notes = models.TextField(blank=True, verbose_name="Muistiinpanot")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Toteuma"
        verbose_name_plural = "Toteumat"

    def __str__(self):
        status = "Kyllä" if self.completed else "Ei"
        return f"{ddmm(self.date)} — {self.get_workout_display()} — toteutui: {status}"