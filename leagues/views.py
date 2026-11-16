from django.shortcuts import render, redirect
from .models import Club, Team, League, Round, LeagueEntry, Match
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_page(request):
    clubs = Club.objects.all().count()
    teams = Team.objects.all().count()
    return render(request, "leagues/dashboard.html", {
        "club_count": clubs,
        "team_count": teams
    })

@login_required
def clubs_page(request):
    errortxt = None
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        city = request.POST.get("city", "").strip()
        logo = request.FILES.get("logo")

                
        if not name :
            errortxt = "اسم باشگاه را وارد کنید!"
        elif Club.objects.filter(name = name).exists():
            errortxt = "این نام باشگاه قبلا ثبت شده است"
        else :
            Club.objects.create(
                name=name,
                city=city,
                logo=logo
            )
            return redirect("clubs") 
        
    clubs = Club.objects.all().order_by("name")

    return render(request, "leagues/clubs.html", {
        "clubs": clubs,
        "error": errortxt,
    })
    
@login_required   
def teams_page(request):
    teams = Team.objects.all().order_by("name")
    club = Club.objects.all().order_by("name")

    
    return render(request, "leagues/teams.html", {
        "teams": teams,
        "clubs": club,
    })
    
@login_required
def matchs_page(request):
    leagues = League.objects.select_related("season").all()
    leagueID = request.GET.get("leagueID")
    
    if leagueID:
        league = League.objects.filter(id=leagueID).first()
    else:
        league = leagues.filter(status=League.Status.ACTIVE).first()
        
    rounds = Round.objects.none()
    
    if league:
        rounds = (
            Round.objects
            .filter(league=league)
            .prefetch_related(
                "matches__home_entry__team__club",
                "matches__away_entry__team__club",
            )
            .order_by("number")
        )

    

    return render(request, "leagues/matchs.html", {
        "league": league,
        "leagues": leagues,
        "rounds": rounds,
    })
    
# /////////////////////////////////
def calculate_standings(league):

    standings = []

    if not league:
        return standings

    entries = LeagueEntry.objects.filter(
        league=league
    ).select_related("team", "team__club")

    stats = {}

    for entry in entries:
        stats[entry.id] = {
            "team": entry.team,
            "played": 0,
            "won": 0,
            "drawn": 0,
            "lost": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
        }

    matches = Match.objects.filter(
        round__league=league,
        status=Match.Status.PLAYED
    ).select_related("home_entry", "away_entry")

    for match in matches:

        home = stats[match.home_entry_id]
        away = stats[match.away_entry_id]

        home_score = match.home_score
        away_score = match.away_score

        home["played"] += 1
        away["played"] += 1

        home["goals_for"] += home_score
        home["goals_against"] += away_score

        away["goals_for"] += away_score
        away["goals_against"] += home_score

        if home_score > away_score:
            home["won"] += 1
            away["lost"] += 1
            home["points"] += league.points_for_win
            away["points"] += league.points_for_loss

        elif home_score < away_score:
            away["won"] += 1
            home["lost"] += 1
            away["points"] += league.points_for_win
            home["points"] += league.points_for_loss

        else:
            home["drawn"] += 1
            away["drawn"] += 1
            home["points"] += league.points_for_draw
            away["points"] += league.points_for_draw

    for item in stats.values():
        item["goal_difference"] = (
            item["goals_for"] - item["goals_against"]
        )

    standings = sorted(
        stats.values(),
        key=lambda item: (
            item["points"],
            item["goal_difference"],
            item["goals_for"],
        ),
        reverse=True
    )

    return standings    
# ////////////////////////

@login_required    
def table_page(request):

    leagues = League.objects.select_related("season").all()

    leagueID = request.GET.get("leagueID")

    if leagueID:
        league = leagues.filter(id=leagueID).first()
    else:
        league = leagues.filter(
            status=League.Status.ACTIVE
        ).first()

    standings = calculate_standings(league)

    return render(request, "leagues/table.html", {
        "league": league,
        "leagues": leagues,
        "standings": standings,
    })
    
    
def view_page(request):

    leagues = League.objects.select_related("season").all()

    leagueID = request.GET.get("leagueID")

    if leagueID:
        league = leagues.filter(id=leagueID).first()
    else:
        league = leagues.filter(
            status=League.Status.ACTIVE
        ).first()

    rounds = Round.objects.none()

    if league:
        rounds = (
            Round.objects
            .filter(league=league)
            .prefetch_related(
                "matches__home_entry__team__club",
                "matches__away_entry__team__club",
            )
            .order_by("number")
        )
    
    results = Match.objects.filter(
        round__league=league,
        status=Match.Status.PLAYED,
        home_score__isnull=False,
        away_score__isnull=False,
    ).select_related(
        "home_entry__team__club",
        "away_entry__team__club",
    ).order_by(
        "-round"
    )[:6]
    
    upcoming_matches = Match.objects.filter(
        round__league=league,
        status=Match.Status.SCHEDULED
    ).select_related(
        "round",
        "home_entry__team__club",
        "away_entry__team__club",
    ).order_by("match_date", "id")

    standings = calculate_standings(league)

    return render(request, "leagues/public_home.html", {
    "leagues": leagues,
    "league": league,
    "rounds": rounds,
    "standings": standings,
    "results": results,
    "upcoming_matches": upcoming_matches,
})
    
    
    
def home_page(request):
    return render(request, "leagues/home.html")