from dataclasses import dataclass

STARTING_RATING = 1500.0 #every team starts here
K_FACTOR = 20.0 #how much ratings move after each game


def expected_score(rating_a, rating_b): #chance team a beats team b based on ratings (standard elo formula)
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


@dataclass
class RatingSnapshot: #one team's rating at one point in time (used for the chart)
    date: object
    team: str
    rating: float


class EloEngine: #keeps track of every team's rating through the season
    def __init__(self, teams, k=K_FACTOR, start=STARTING_RATING):
        self.ratings = {t: start for t in teams}
        self.k = k
        self.history = []
        for t in teams:
            self.history.append(RatingSnapshot(date=None, team=t, rating=start))

    def process_game(self, home_team, away_team, home_score, away_score, game_date=None):
        r_home = self.ratings[home_team]
        r_away = self.ratings[away_team]

        actual_home = 1.0 if home_score > away_score else 0.0
        expected_home = expected_score(r_home, r_away)

        change = self.k * (actual_home - expected_home) #big change for upsets, small change for expected wins
        self.ratings[home_team] = r_home + change
        self.ratings[away_team] = r_away - change #whatever one team gains the other loses

        self.history.append(RatingSnapshot(date=game_date, team=home_team, rating=self.ratings[home_team]))
        self.history.append(RatingSnapshot(date=game_date, team=away_team, rating=self.ratings[away_team]))

    def process_games(self, games):
        for g in games:
            self.process_game(g.home_team, g.away_team, g.home_score, g.away_score, g.date)

    def rankings(self): #teams sorted best to worst
        return sorted(self.ratings.items(), key=lambda kv: kv[1], reverse=True)


def compute_regular_season_ratings(league): #runs elo over every regular season game in order
    engine = EloEngine(teams=league.teams)
    engine.process_games(league.regular_season_games)
    return engine


if __name__ == "__main__":
    from data import load_league

    league = load_league("league_source.xlsx")
    engine = compute_regular_season_ratings(league)

    print("Final Elo ratings after the regular season:\n")
    for rank, (team, rating) in enumerate(engine.rankings(), start=1):
        print(f"{rank}. {team:<15} {rating:.0f}")
