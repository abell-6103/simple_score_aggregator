"""
Contains the Scorecard class which stores the data of the score from any given game.
Scorecard contains team names, abbreviations, scores, game status, and the date the game was played. Some or all fields may be set to None.
"""

from datetime import date
try:
    import pandas as pd
    pd_enabled = True
except ImportError | ModuleNotFoundError as e:
    pd_exception = e
    pd_enabled = False

class Scorecard:
    def __init__(self) -> None:
        self.name_team1 = None
        self.name_team2 = None

        self.abbr_team1 = None
        self.abbr_team2 = None

        self.score_team1 = None
        self.score_team2 = None

        self.game_state = None

        self.date = None

    def __repr__(self) -> str:
        score_str = ""

        if self.abbr_team1 is not None and self.abbr_team2 is not None:
            score_str += f'| {self.abbr_team1}'
            if self.score_team1 is not None and self.score_team2 is not None:
                score_str += f' {self.score_team1} - {self.score_team2} {self.abbr_team2}'
            else:
                score_str += f' @ {self.abbr_team2}'
        elif self.name_team1 is not None and self.name_team2 is not None:
            score_str += f'| {self.name_team1}'
            if self.score_team1 is not None and self.score_team2 is not None:
                score_str += f' {self.score_team1} - {self.score_team2} {self.name_team2}'
            else:
                score_str += f' @ {self.name_team2}'
        
        if self.game_state is not None:
            score_str += f' | {self.game_state}'
        
        if self.date is not None:
            score_str += f' ({str(self.date)})'

        return score_str

    def __ge__(self, other: 'Scorecard'):
        self_state = self.game_state
        other_state = other.game_state

        if self_state is None:
            self_state = ''
        if other_state is None:
            other_state = ''

        return self_state >= other_state
    
    def __lt__(self, other: 'Scorecard') -> bool:
        return not self.__ge__(other)

    def setNames(self, name_team1: str, name_team2: str) -> None:
        self.name_team1 = name_team1
        self.name_team2 = name_team2

    def setAbbrs(self, abbr_team1: str, abbr_team2: str) -> None:
        self.abbr_team1 = abbr_team1
        self.abbr_team2 = abbr_team2

    def setScore(self, score_team1: int, score_team2: int) -> None:
        if score_team1 is not None:
            score_team1 = int(score_team1)
        if score_team2 is not None:
            score_team2 = int(score_team2)

        self.score_team1 = score_team1
        self.score_team2 = score_team2

    def setState(self, state: str) -> None:
        self.game_state = state

    def setDate(self, day: date) -> None:
        self.date = day

    def getDict(self) -> dict:
        return {
            'away_team_name' : self.name_team1,
            'away_team_abbr' : self.abbr_team1,
            'away_team_score' : self.score_team1,
            'home_team_name' : self.name_team2,
            'home_team_abbr' : self.abbr_team2,
            'home_team_score' : self.score_team2,
            'game_state' : self.game_state,
            'game_date' : str(self.date)
        }
    
    def getSeries(self) -> pd.Series:
        score_dict = self.getDict()
        if pd_enabled:
            ds = pd.Series(score_dict,index=score_dict.keys())
            return ds
        raise pd_exception