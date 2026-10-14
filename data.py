from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass
class Game: #one game from the schedule
    game_id: str
    date: date
    stage: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int

    @property
    def is_regular_season(self):
        return self.stage == "Regular Season"

    @property
    def winner(self): #calculated from the score, not stored
        return self.home_team if self.home_score > self.away_score else self.away_team

    @property
    def loser(self):
        return self.away_team if self.home_score > self.away_score else self.home_team

    @property
    def margin(self): #how many points the game was decided by
        return abs(self.home_score - self.away_score)


@dataclass
class PlayerGame: #one player's stat line for one game
    game_id: str
    date: date
    team: str
    player: str
    pts: float
    reb: float
    ast: float
    stl: float
    blk: float
    tpm: float

    @property
    def played(self): #false if the row is just an empty roster spot
        return any(v is not None for v in (self.pts, self.reb, self.ast, self.stl, self.blk, self.tpm))

    @property
    def eff(self): #pts+reb+ast+stl+blk, skips any blank stats instead of crashing
        vals = [v for v in (self.pts, self.reb, self.ast, self.stl, self.blk) if v is not None]
        return sum(vals)


@dataclass
class League: #everything from the spreadsheet in one place
    games: list
    player_games: list
    teams: list

    @property
    def regular_season_games(self):
        return sorted([g for g in self.games if g.is_regular_season], key=lambda g: g.date)

    @property
    def playoff_games(self):
        return sorted([g for g in self.games if not g.is_regular_season], key=lambda g: g.date)

    def games_for_team(self, team):
        return [g for g in self.games if team in (g.home_team, g.away_team)]

    def player_games_for(self, player):
        return sorted(
            (pg for pg in self.player_games if pg.player == player and pg.played),
            key=lambda pg: pg.date,
        )

    def all_players(self):
        return sorted({pg.player for pg in self.player_games if pg.played})


def _nan_to_none(v): #blank cells come in as NaN, turn them into None
    return None if pd.isna(v) else v


def load_league(path): #reads the spreadsheet and turns it into Game and PlayerGame objects
    xls = pd.ExcelFile(path)

    sched = pd.read_excel(xls, "Schedule", header=1) #header is on the 2nd row of the sheet
    sched = sched.dropna(subset=["Game ID", "Home Team Score", "Away Team Score"])

    games = []
    for _, row in sched.iterrows():
        games.append(Game(
            game_id=row["Game ID"],
            date=pd.to_datetime(row["Date"]).date(),
            stage=str(row["Stage"]).strip(),
            home_team=str(row["Home Team"]).strip(),
            away_team=str(row["Away Team"]).strip(),
            home_score=int(row["Home Team Score"]),
            away_score=int(row["Away Team Score"]),
        ))

    allstats = pd.read_excel(xls, "AllStats")
    allstats = allstats.dropna(subset=["Player"])

    date_by_game = {g.game_id: g.date for g in games}

    team_name_by_code = {} #box scores only have team codes (T1, T2...) so map them to real names
    teams_df = pd.read_excel(xls, "Teams", header=1)
    for _, row in teams_df.iterrows():
        code = row.get("Team Code (DO NOT EDIT)")
        name = row.get("TEAM NAME (EDITABLE)")
        if pd.notna(code) and pd.notna(name):
            team_name_by_code[str(code).strip()] = str(name).strip()

    player_games = []
    for _, row in allstats.iterrows():
        gid = row["GameID"]
        team_code = str(row["TeamCode"]).strip()
        player_games.append(PlayerGame(
            game_id=gid,
            date=date_by_game.get(gid, pd.to_datetime(row["Date"]).date()),
            team=team_name_by_code.get(team_code, team_code),
            player=str(row["Player"]).strip(),
            pts=_nan_to_none(row["PTS"]),
            reb=_nan_to_none(row["REB"]),
            ast=_nan_to_none(row["AST"]),
            stl=_nan_to_none(row["STL"]),
            blk=_nan_to_none(row["BLK"]),
            tpm=_nan_to_none(row["3PM"]),
        ))

    teams = sorted(team_name_by_code.values())
    return League(games=games, player_games=player_games, teams=teams)


if __name__ == "__main__":
    league = load_league("league_source.xlsx")
    print(f"{len(league.games)} games loaded "
          f"({len(league.regular_season_games)} regular season, {len(league.playoff_games)} playoff)")
    print(f"{len(league.teams)} teams:", league.teams)
    print(f"{len(league.all_players())} players with recorded stats")
