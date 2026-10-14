import random
from collections import Counter

from bracket import next_power_of_2, simulate_bracket, monte_carlo_playoffs


def test_next_power_of_2():
    assert next_power_of_2(1) == 1
    assert next_power_of_2(2) == 2
    assert next_power_of_2(3) == 4
    assert next_power_of_2(7) == 8
    assert next_power_of_2(8) == 8
    assert next_power_of_2(9) == 16


def test_bracket_champion_is_one_of_the_entrants():
    seeds = [(1, "A"), (2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")]
    ratings = {name: 1500 for _, name in seeds}
    rng = random.Random(1)
    champ = simulate_bracket(seeds, ratings, rng)
    assert champ in {name for _, name in seeds}


def test_bracket_is_deterministic_given_a_seeded_rng():
    seeds = [(1, "A"), (2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")]
    ratings = {"A": 1600, "B": 1550, "C": 1500, "D": 1480, "E": 1460, "F": 1440, "G": 1420}
    champ1 = simulate_bracket(seeds, ratings, random.Random(99))
    champ2 = simulate_bracket(seeds, ratings, random.Random(99))
    assert champ1 == champ2


def test_two_team_bracket_is_a_single_game():
    seeds = [(1, "A"), (2, "B")]
    ratings = {"A": 2000, "B": 1000}
    rng = random.Random(0)
    wins = Counter(simulate_bracket(seeds, ratings, rng) for _ in range(500))
    assert wins["A"] > wins["B"]


def test_heavy_favorite_wins_monte_carlo_most_often():
    seeds = [(1, "Best"), (2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")]
    ratings = {"Best": 2000, "B": 1500, "C": 1500, "D": 1500, "E": 1500, "F": 1500, "G": 1500}
    probs = monte_carlo_playoffs(seeds, ratings, n_sims=2000, seed=7)

    assert probs["Best"] > 1 / 7
    assert probs["Best"] == max(probs.values())


def test_monte_carlo_probabilities_sum_to_one():
    seeds = [(1, "A"), (2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")]
    ratings = {name: 1500 + i * 10 for i, (_, name) in enumerate(seeds)}
    probs = monte_carlo_playoffs(seeds, ratings, n_sims=1000, seed=3)

    assert abs(sum(probs.values()) - 1.0) < 1e-9
