import argparse

from bracket import compute_standings, monte_carlo_playoffs
from data import load_league
from elo import compute_regular_season_ratings
from player_stats import all_profiles, build_profile
from team_stats import team_awards as get_team_awards
from team_stats import win_impact
from visualize import plot_championship_probs, plot_elo_history, plot_player_trend

DATA_PATH = "league_source.xlsx"


def cmd_ratings(args): #python main.py ratings
    league = load_league(DATA_PATH)
    engine = compute_regular_season_ratings(league)

    print("\nFinal Elo ratings after the regular season:\n")
    for rank, (team, rating) in enumerate(engine.rankings(), start=1):
        print(f"  {rank}. {team:<15} {rating:.0f}")

    path = plot_elo_history(engine)
    print(f"\nSaved chart to {path}")


def cmd_simulate(args): #python main.py simulate --n 20000
    league = load_league(DATA_PATH)
    engine = compute_regular_season_ratings(league)

    seeds = compute_standings(league)
    print("\nPlayoff seeding:")
    for seed, team in seeds:
        print(f"  {seed}. {team}")

    print(f"\nRunning {args.n:,} simulated playoff brackets...")
    probs = monte_carlo_playoffs(seeds, engine.ratings, n_sims=args.n)

    print("\nChampionship probability:\n")
    for team, p in sorted(probs.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:<15} {p * 100:5.1f}%")

    path = plot_championship_probs(probs)
    print(f"\nSaved chart to {path}")


def cmd_player(args): #python main.py player "Player 04"
    league = load_league(DATA_PATH)
    profile = build_profile(league, args.name)
    if profile is None:
        print(f"No recorded games found for '{args.name}'.")
        print("Known players:", ", ".join(league.all_players()))
        return

    print(f"\n{profile.name} — {profile.games_played} games played\n")
    print(f"  PTS/G: {profile.pts_avg:.1f}   REB/G: {profile.reb_avg:.1f}   "
          f"AST/G: {profile.ast_avg:.1f}   STL/G: {profile.stl_avg:.1f}   "
          f"BLK/G: {profile.blk_avg:.1f}   3PM: {profile.tpm_total}")
    print(f"  EFF/G: {profile.eff_avg:.1f}")
    print(f"  Consistency: ±{profile.consistency:.1f} EFF (lower = steadier)")
    print(f"  Recent form (last 3 vs season avg): {profile.recent_form:+.1f}")
    print(f"  Best game: {profile.best_game_eff:.0f} EFF on {profile.best_game_date}")

    path = plot_player_trend(league, args.name)
    print(f"\nSaved chart to {path}")


def cmd_awards(args): #python main.py awards
    league = load_league(DATA_PATH)
    profiles = all_profiles(league, min_games=3)

    print("\n=== Individual Awards (min 3 GP) ===\n")
    mvp = max(profiles, key=lambda p: p.eff_avg)
    print(f"MVP:              {mvp.name} ({mvp.eff_avg:.1f} EFF/G)")

    steady = [p for p in profiles if p.games_played >= 4]
    consistent = min(steady, key=lambda p: p.consistency)
    print(f"Most Consistent:  {consistent.name} (±{consistent.consistency:.1f} EFF variance)")

    hot = max(profiles, key=lambda p: p.recent_form)
    print(f"Hottest Streak:   {hot.name} ({hot.recent_form:+.1f} EFF/G above their own average)")

    best_game = max(profiles, key=lambda p: p.best_game_eff)
    print(f"Best Single Game: {best_game.name} ({best_game.best_game_eff:.0f} EFF on {best_game.best_game_date})")

    impact = win_impact(league)
    if impact:
        name, corr, n = impact[0]
        print(f"Win Impact:       {name} (r = {corr:+.2f} between their EFF and team margin, {n} games)")


def cmd_team_awards(args): #python main.py team-awards
    league = load_league(DATA_PATH)
    awards = get_team_awards(league)

    print("\n=== Team Awards ===\n")
    team, ppg = awards["best_offense"]
    print(f"Best Offense:       {team} ({ppg:.1f} PPG)")
    team, papg = awards["best_defense"]
    print(f"Best Defense:       {team} ({papg:.1f} opponent PPG)")
    g = awards["closest_game"]
    print(f"Closest Game:       {g.home_team} {g.home_score}-{g.away_score} {g.away_team} ({g.date})")
    g = awards["biggest_blowout"]
    print(f"Biggest Blowout:    {g.home_team} {g.home_score}-{g.away_score} {g.away_team} (by {g.margin})")
    team, streak = awards["longest_win_streak"]
    print(f"Longest Win Streak: {team} ({streak} games)")


def main(): #sets up the commands and runs whichever one was typed
    parser = argparse.ArgumentParser(description="Rec league rating & simulation engine")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ratings", help="Show Elo ratings and save a rating-history chart")

    p_sim = sub.add_parser("simulate", help="Monte Carlo simulate the playoffs")
    p_sim.add_argument("--n", type=int, default=20000, help="Number of simulated brackets")

    p_player = sub.add_parser("player", help="Show one player's profile and trend chart")
    p_player.add_argument("name", help="Player's full name")

    sub.add_parser("awards", help="Show individual season awards")
    sub.add_parser("team-awards", help="Show team-level season awards")

    args = parser.parse_args()
    if args.command == "ratings":
        cmd_ratings(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    elif args.command == "player":
        cmd_player(args)
    elif args.command == "awards":
        cmd_awards(args)
    elif args.command == "team-awards":
        cmd_team_awards(args)


if __name__ == "__main__":
    main()
