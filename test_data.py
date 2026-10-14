from datetime import date

from data import PlayerGame


def make_pg(pts=None, reb=None, ast=None, stl=None, blk=None, tpm=None): #makes a fake player game, all stats blank unless i pass them in
    return PlayerGame("G01", date(2026, 3, 4), "A", "Test Player", pts, reb, ast, stl, blk, tpm)


def test_played_is_false_when_all_stats_are_none():
    pg = make_pg()
    assert pg.played is False


def test_played_is_true_with_a_single_recorded_stat():
    pg = make_pg(pts=2)
    assert pg.played is True


def test_eff_treats_missing_categories_as_zero_not_an_error(): #this used to crash before the fix (some stats filled in, some blank)
    pg = make_pg(pts=14, reb=6, ast=3, stl=2, blk=None, tpm=None)
    assert pg.eff == 14 + 6 + 3 + 2


def test_eff_is_zero_when_nothing_recorded():
    pg = make_pg()
    assert pg.eff == 0
