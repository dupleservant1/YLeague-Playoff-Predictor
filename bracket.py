import random
from collections import Counter

from elo import expected_score


def next_power_of_2(n): #finds the bracket size for playoffs(finds how many byes are needed for)
    p = 1
    while p < n:
        p *= 2
    return p


def compute_standings(league): #creates the seeding, based on three factors: wins, point differential, and point total
    wins = Counter()
    point_diff = Counter()
    points_for = Counter()

    for g in league.regular_season_games:
        wins[g.winner] += 1
        point_diff[g.home_team] += g.home_score - g.away_score
        point_diff[g.away_team] += g.away_score - g.home_score
        points_for[g.home_team] += g.home_score
        points_for[g.away_team] += g.away_score

    ordered = sorted(
        league.teams,
        key=lambda t: (wins[t], point_diff[t], points_for[t]),
        reverse=True,
    )
    return [(i + 1, team) for i, team in enumerate(ordered)]


def simulate_bracket(seeds, ratings, rng): #plays out one full playoff and returns the champion
    remaining = sorted(seeds, key=lambda x: x[0]) #put teams in seed order

    while len(remaining) > 1:
        n = len(remaining)
        target = next_power_of_2(n)
        byes = target - n #top seeds get the byes

        byes_teams = remaining[:byes]
        playing = remaining[byes:]

        winners = []
        i, j = 0, len(playing) - 1 #best seed left plays worst seed left
        while i < j:
            seed_a, team_a = playing[i]
            seed_b, team_b = playing[j]
            p_a = expected_score(ratings[team_a], ratings[team_b]) #team a's chance to win based on elo
            winner = (seed_a, team_a) if rng.random() < p_a else (seed_b, team_b) #random number decides the game, weighted by elo
            winners.append(winner)
            i += 1
            j -= 1

        remaining = sorted(byes_teams + winners, key=lambda x: x[0]) #re-sort every round so the 1 seed always plays the lowest seed left

    return remaining[0][1]


def monte_carlo_playoffs(seeds, ratings, n_sims=20000, seed=42): #runs the bracket 20,000 times and counts how often each team wins
    rng = random.Random(seed) #same seed = same results every run
    champions = Counter()

    for _ in range(n_sims):
        champ = simulate_bracket(seeds, ratings, rng)
        champions[champ] += 1

    return {team: champions[team] / n_sims for _, team in seeds}


if __name__ == "__main__":
    from data import load_league
    from elo import compute_regular_season_ratings

    league = load_league("league_source.xlsx")
    engine = compute_regular_season_ratings(league)

    seeds = compute_standings(league)
    print("Playoff seeding (from regular-season record):")
    for seed, team in seeds:
        print(f"  {seed}. {team}  (Elo {engine.ratings[team]:.0f})")

    print(f"\nRunning 20,000 simulated playoff brackets...\n")
    probs = monte_carlo_playoffs(seeds, engine.ratings, n_sims=20000)
    print("Championship probability:")
    for team, p in sorted(probs.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:<15} {p * 100:5.1f}%")

    actual_champion = sorted(league.playoff_games, key=lambda g: g.date)[-1].winner #winner of the last playoff game = real champion
    print(f"\nWhat actually happened: {actual_champion} won the championship.")
