from django.contrib import admin


from django.contrib import admin
from .models import (
    Club,
    AgeGroup,
    Team,
    Season,
    League,
    LeagueEntry,
    Round,
    Match,
)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "created_at")
    search_fields = ("name", "city")
    ordering = ("name",)


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    search_fields = ("name",)
    ordering = ("sort_order",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "age_group", "created_at")
    list_filter = ("age_group", "club")
    search_fields = ("name", "club__name")
    autocomplete_fields = ("club", "age_group")


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class LeagueEntryInline(admin.TabularInline):
    model = LeagueEntry
    extra = 1
    autocomplete_fields = ("team",)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "season", "age_group", "status")
    list_filter = ("season", "age_group", "status")
    search_fields = ("name",)
    autocomplete_fields = ("season", "age_group")
    inlines = (LeagueEntryInline,)


@admin.register(LeagueEntry)
class LeagueEntryAdmin(admin.ModelAdmin):
    list_display = ("league", "team", "registered_at")
    list_filter = ("league",)
    search_fields = ("league__name", "team__name", "team__club__name")
    autocomplete_fields = ("league", "team")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("league", "number", "name", "start_date", "end_date")
    list_filter = ("league",)
    search_fields = ("league__name", "name")
    autocomplete_fields = ("league",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "round",
        "home_entry",
        "away_entry",
        "match_date",
        "status",
        "home_score",
        "away_score",
    )
    list_filter = ("status", "round__league", "round__number")
    search_fields = (
        "home_entry__team__name",
        "away_entry__team__name",
        "home_entry__team__club__name",
        "away_entry__team__club__name",
    )
    autocomplete_fields = ("round", "home_entry", "away_entry")
    list_per_page = 25
