import statistics
from dataclasses import dataclass


@dataclass
class PlayerProfile: #a player's season summary
    name: str
    games_played: int
    pts_avg: float
    reb_avg: float
    ast_avg: float
    stl_avg: float
    blk_avg: float
    tpm_total: int
    eff_avg: float
    consistency: float
    recent_form: float
    best_game_eff: float
    best_game_date: object


def build_profile(league, player, recent_window=3): #builds a player's season stats from their game logs
    games = league.player_games_for(player)
    if not games:
        return None

    effs = [g.eff for g in games]
    n = len(games)

    def avg(attr):
        vals = [getattr(g, attr) for g in games if getattr(g, attr) is not None]
        return sum(vals) / len(vals) if vals else 0.0

    season_eff_avg = sum(effs) / n
    consistency = statistics.pstdev(effs) if n > 1 else 0.0 #std dev of eff, lower = more consistent

    recent = games[-recent_window:] #last 3 games
    recent_avg = sum(g.eff for g in recent) / len(recent)
    recent_form = recent_avg - season_eff_avg

    best_game = max(games, key=lambda g: g.eff)

    return PlayerProfile(
        name=player,
        games_played=n,
        pts_avg=avg("pts"), reb_avg=avg("reb"), ast_avg=avg("ast"),
        stl_avg=avg("stl"), blk_avg=avg("blk"),
        tpm_total=int(sum(g.tpm for g in games if g.tpm is not None)),
        eff_avg=season_eff_avg,
        consistency=consistency,
        recent_form=recent_form,
        best_game_eff=best_game.eff,
        best_game_date=best_game.date,
    )


def all_profiles(league, min_games=1): #profile for every player with at least min_games
    profiles = []
    for name in league.all_players():
        p = build_profile(league, name)
        if p and p.games_played >= min_games:
            profiles.append(p)
    return profiles


if __name__ == "__main__":
    from data import load_league

    league = load_league("league_source.xlsx")
    profiles = all_profiles(league, min_games=3)

    print("MVP race (by EFF/G, min 3 GP):\n")
    for p in sorted(profiles, key=lambda p: p.eff_avg, reverse=True)[:10]:
        print(f"  {p.name:<20} {p.eff_avg:5.1f} EFF/G   "
              f"(consistency ±{p.consistency:4.1f}, recent form {p.recent_form:+4.1f})")

    print("\nMost consistent (lowest variance, min 4 GP):\n")
    steady = [p for p in profiles if p.games_played >= 4]
    for p in sorted(steady, key=lambda p: p.consistency)[:5]:
        print(f"  {p.name:<20} ±{p.consistency:.1f} EFF variance   ({p.eff_avg:.1f} EFF/G avg)")

    print("\nHottest right now (last 3 games vs season average):\n")
    for p in sorted(profiles, key=lambda p: p.recent_form, reverse=True)[:5]:
        print(f"  {p.name:<20} {p.recent_form:+.1f} EFF/G above their own average")
