from elo import EloEngine, expected_score


def test_equal_ratings_give_fifty_fifty_odds():
    assert expected_score(1500, 1500) == 0.5


def test_expected_scores_sum_to_one():
    a, b = 1620, 1480
    assert abs(expected_score(a, b) + expected_score(b, a) - 1.0) < 1e-9


def test_higher_rating_is_favored():
    assert expected_score(1600, 1400) > 0.5
    assert expected_score(1400, 1600) < 0.5


def test_rating_change_is_zero_sum():
    engine = EloEngine(teams=["A", "B"])
    r_home_before = engine.ratings["A"]
    r_away_before = engine.ratings["B"]

    engine.process_game("A", "B", home_score=60, away_score=50)

    home_change = engine.ratings["A"] - r_home_before
    away_change = engine.ratings["B"] - r_away_before
    assert abs(home_change + away_change) < 1e-9


def test_winning_increases_rating_against_equal_opponent():
    engine = EloEngine(teams=["A", "B"])
    engine.process_game("A", "B", home_score=60, away_score=50)
    assert engine.ratings["A"] > 1500
    assert engine.ratings["B"] < 1500


def test_upset_moves_rating_more_than_an_expected_win(): #beating a better team should move your rating more
    favorite_wins = EloEngine(teams=["A", "B"])
    favorite_wins.ratings["A"] = 1700
    favorite_wins.ratings["B"] = 1300
    favorite_wins.process_game("A", "B", home_score=60, away_score=50)
    favorite_change = favorite_wins.ratings["A"] - 1700

    upset = EloEngine(teams=["A", "B"])
    upset.ratings["A"] = 1300
    upset.ratings["B"] = 1700
    upset.process_game("A", "B", home_score=60, away_score=50)
    upset_change = upset.ratings["A"] - 1300

    assert upset_change > favorite_change > 0


def test_process_games_runs_in_order_and_is_deterministic():
    from types import SimpleNamespace

    games = [
        SimpleNamespace(home_team="A", away_team="B", home_score=60, away_score=50, date="d1"),
        SimpleNamespace(home_team="B", away_team="A", home_score=55, away_score=52, date="d2"),
    ]
    e1 = EloEngine(teams=["A", "B"])
    e1.process_games(games)
    e2 = EloEngine(teams=["A", "B"])
    e2.process_games(games)
    assert e1.ratings == e2.ratings
