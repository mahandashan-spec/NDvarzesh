from django.db import models

from django.core.exceptions import ValidationError
from django.db.models import Q


class Club(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="نام باشگاه")
    city = models.CharField(max_length=100, default="تبریز", verbose_name="شهر")
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(
    upload_to="team_logos/",
    blank=True,
    null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "باشگاه"
        verbose_name_plural = "باشگاه‌ها"

    def __str__(self):
        return self.name


class AgeGroup(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="رده سنی")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "رده سنی"
        verbose_name_plural = "رده‌های سنی"

    def __str__(self):
        return self.name


class Team(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name="teams",
        verbose_name="باشگاه",
    )
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.PROTECT,
        related_name="teams",
        verbose_name="رده سنی",
    )
    name = models.CharField(max_length=100, verbose_name="نام تیم")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["club__name", "age_group__sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["club", "age_group", "name"],
                name="unique_team_per_club_age_name",
            )
        ]
        verbose_name = "تیم"
        verbose_name_plural = "تیم‌ها"

    def __str__(self):
        return f"{self.club.name} - {self.name} ({self.age_group.name})"


class Season(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="نام فصل",
        help_text="مثلاً ۱۴۰۵-۱۴۰۶",
    )
    start_date = models.DateField(null=True, blank=True, verbose_name="تاریخ شروع")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاریخ پایان")
    is_active = models.BooleanField(default=True, verbose_name="فصل فعال")

    class Meta:
        ordering = ["-id"]
        verbose_name = "فصل"
        verbose_name_plural = "فصل‌ها"

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("تاریخ پایان نباید قبل از تاریخ شروع باشد.")


class League(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        ACTIVE = "active", "در حال برگزاری"
        COMPLETED = "completed", "پایان‌یافته"

    name = models.CharField(max_length=150, verbose_name="نام لیگ")
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name="leagues",
        verbose_name="فصل",
    )
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.PROTECT,
        related_name="leagues",
        verbose_name="رده سنی",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )
    points_for_win = models.PositiveSmallIntegerField(
        default=3, verbose_name="امتیاز برد"
    )
    points_for_draw = models.PositiveSmallIntegerField(
        default=1, verbose_name="امتیاز مساوی"
    )
    points_for_loss = models.PositiveSmallIntegerField(
        default=0, verbose_name="امتیاز باخت"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "season", "age_group"],
                name="unique_league_season_age",
            )
        ]
        verbose_name = "لیگ"
        verbose_name_plural = "لیگ‌ها"

    def __str__(self):
        return f"{self.name} - {self.season.name} - {self.age_group.name}"


class LeagueEntry(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="لیگ",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="league_entries",
        verbose_name="تیم",
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["team__club__name", "team__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["league", "team"],
                name="unique_team_in_league",
            )
        ]
        verbose_name = "تیم شرکت‌کننده"
        verbose_name_plural = "تیم‌های شرکت‌کننده"

    def clean(self):
        if self.league_id and self.team_id:
            if self.league.age_group_id != self.team.age_group_id:
                raise ValidationError(
                    "رده سنی تیم باید با رده سنی لیگ یکسان باشد."
                )

    def __str__(self):
        return f"{self.league.name} - {self.team.name}"


class Round(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="rounds",
        verbose_name="لیگ",
    )
    number = models.PositiveIntegerField(verbose_name="شماره هفته")
    name = models.CharField(max_length=100, blank=True, verbose_name="عنوان")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاریخ شروع")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاریخ پایان")

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["league", "number"],
                name="unique_round_number_per_league",
            ),
            models.CheckConstraint(
                condition=Q(number__gte=1),
                name="round_number_gte_one",
            ),
        ]
        verbose_name = "هفته"
        verbose_name_plural = "هفته‌ها"

    def clean(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("تاریخ پایان هفته نباید قبل از شروع باشد.")

    def __str__(self):
        return f"{self.league.name} - هفته {self.number}"


class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "برنامه‌ریزی‌شده"
        PLAYED = "played", "برگزارشده"
        POSTPONED = "postponed", "به‌تعویق‌افتاده"
        CANCELLED = "cancelled", "لغوشده"

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="هفته",
    )
    home_entry = models.ForeignKey(
        LeagueEntry,
        on_delete=models.PROTECT,
        related_name="home_matches",
        verbose_name="تیم میزبان",
    )
    away_entry = models.ForeignKey(
        LeagueEntry,
        on_delete=models.PROTECT,
        related_name="away_matches",
        verbose_name="تیم میهمان",
    )
    match_date = models.DateTimeField(
        null=True, blank=True, verbose_name="تاریخ و ساعت مسابقه"
    )
    venue = models.CharField(max_length=150, blank=True, verbose_name="محل مسابقه")
    home_score = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="گل میزبان"
    )
    away_score = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="گل میهمان"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name="وضعیت مسابقه",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["match_date", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(home_entry=models.F("away_entry")),
                name="match_teams_must_differ",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="played", home_score__isnull=False,
                      away_score__isnull=False)
                    | (
                        ~Q(status="played")
                        & Q(home_score__isnull=True, away_score__isnull=True)
                    )
                ),
                name="match_score_consistent_with_status",
            ),
        ]
        verbose_name = "مسابقه"
        verbose_name_plural = "مسابقات"

    def clean(self):
        errors = {}

        if self.home_entry_id and self.away_entry_id:
            if self.home_entry_id == self.away_entry_id:
                errors["away_entry"] = "یک تیم نمی‌تواند مقابل خودش بازی کند."

        if self.round_id and self.home_entry_id:
            if self.round.league_id != self.home_entry.league_id:
                errors["home_entry"] = "تیم میزبان عضو لیگ این هفته نیست."

        if self.round_id and self.away_entry_id:
            if self.round.league_id != self.away_entry.league_id:
                errors["away_entry"] = "تیم میهمان عضو لیگ این هفته نیست."

        if self.status == self.Status.PLAYED:
            if self.home_score is None or self.away_score is None:
                errors["home_score"] = "برای مسابقه برگزارشده باید نتیجه ثبت شود."
        elif self.home_score is not None or self.away_score is not None:
            errors["home_score"] = (
                "تا زمانی که وضعیت مسابقه برگزارشده نیست، "
                "باید نتیجه ثبت‌نشده باشد."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.home_entry.team.name} - "
            f"{self.away_entry.team.name}"
        )
