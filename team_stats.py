import statistics
from collections import defaultdict


def team_awards(league): #best offense/defense, closest game, biggest blowout, longest win streak
    games = league.regular_season_games

    pf = defaultdict(int)
    pa = defaultdict(int)
    gp = defaultdict(int)

    for g in games:
        pf[g.home_team] += g.home_score
        pa[g.home_team] += g.away_score
        gp[g.home_team] += 1
        pf[g.away_team] += g.away_score
        pa[g.away_team] += g.home_score
        gp[g.away_team] += 1

    ppg = {t: pf[t] / gp[t] for t in league.teams if gp[t]}
    papg = {t: pa[t] / gp[t] for t in league.teams if gp[t]}

    best_offense = max(ppg, key=ppg.get)
    best_defense = min(papg, key=papg.get)

    closest = min(games, key=lambda g: g.margin)
    blowout = max(games, key=lambda g: g.margin)

    streaks = {}
    for team in league.teams:
        best = cur = 0
        for g in sorted(league.games_for_team(team), key=lambda g: g.date):
            if not g.is_regular_season:
                continue
            if g.winner == team:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        streaks[team] = best
    streak_leader = max(streaks, key=streaks.get)

    return {
        "best_offense": (best_offense, ppg[best_offense]),
        "best_defense": (best_defense, papg[best_defense]),
        "closest_game": closest,
        "biggest_blowout": blowout,
        "longest_win_streak": (streak_leader, streaks[streak_leader]),
    }


def win_impact(league, min_games=4): #does a player's eff go up when their team wins big? (small samples so just a rough signal)
    margin_by_team_game = {}
    for g in league.games:
        margin_by_team_game[(g.game_id, g.home_team)] = g.home_score - g.away_score
        margin_by_team_game[(g.game_id, g.away_team)] = g.away_score - g.home_score

    results = []
    for name in league.all_players():
        games = league.player_games_for(name)
        if len(games) < min_games:
            continue
        effs, margins = [], []
        for pg in games:
            m = margin_by_team_game.get((pg.game_id, pg.team))
            if m is not None:
                effs.append(pg.eff)
                margins.append(m)
        if len(effs) < min_games or len(set(effs)) < 2 or len(set(margins)) < 2:
            continue
        corr = statistics.correlation(effs, margins) #correlation between player eff and team margin
        results.append((name, corr, len(effs)))

    return sorted(results, key=lambda r: r[1], reverse=True)


if __name__ == "__main__":
    from data import load_league

    league = load_league("league_source.xlsx")

    print("=== Team Awards ===\n")
    awards = team_awards(league)
    team, ppg = awards["best_offense"]
    print(f"Best Offense:      {team} ({ppg:.1f} PPG)")
    team, papg = awards["best_defense"]
    print(f"Best Defense:      {team} ({papg:.1f} opp PPG)")
    g = awards["closest_game"]
    print(f"Closest Game:      {g.home_team} {g.home_score} - {g.away_score} {g.away_team} ({g.date})")
    g = awards["biggest_blowout"]
    print(f"Biggest Blowout:   {g.home_team} {g.home_score} - {g.away_score} {g.away_team} ({g.date}, by {g.margin})")
    team, streak = awards["longest_win_streak"]
    print(f"Longest Win Streak: {team} ({streak} games)")

    print("\n=== Win Impact (correlation between player EFF and team margin) ===\n")
    for name, corr, n in win_impact(league)[:10]:
        print(f"  {name:<20} r = {corr:+.2f}   ({n} games)")
