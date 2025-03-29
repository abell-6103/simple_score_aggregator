"""
Contains the Scorecard class which stores the data of the score from any given game.
Scorecard contains team names, abbreviations, scores, game status, and the date the game was played. Some or all fields may be set to None.
"""

from datetime import date
import pandas as pd

class Scorecard:
    def __init__(self):
        self.name_team1 = None
        self.name_team2 = None

        self.abbr_team1 = None
        self.abbr_team2 = None

        self.score_team1 = None
        self.score_team2 = None

        self.game_state = None

        self.date = None

    def __repr__(self):
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

    def __ge__(self,other):
        if not isinstance(other,Scorecard):
            raise TypeError('Cannot compare scorecard to non-scorecard')
        
        self_state = self.game_state
        other_state = other.game_state

        if self_state is None:
            self_state = ''
        if other_state is None:
            other_state = ''

        return self_state >= other_state
    
    def __lt__(self,other):
        return not self.__ge__(other)

    def setNames(self,name_team1,name_team2):
        self.name_team1 = name_team1
        self.name_team2 = name_team2

    def setAbbrs(self,abbr_team1,abbr_team2):
        self.abbr_team1 = abbr_team1
        self.abbr_team2 = abbr_team2

    def setScore(self,score_team1,score_team2):
        if score_team1 is not None:
            score_team1 = int(score_team1)
        if score_team2 is not None:
            score_team2 = int(score_team2)

        self.score_team1 = score_team1
        self.score_team2 = score_team2

    def setState(self,state):
        self.game_state = state

    def setDate(self,day):
        if not isinstance(day,date):
            raise TypeError('Expected date object')
        self.date = day

    def getDict(self):
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
    
    def getSeries(self):
        score_dict = self.getDict()
        ds = pd.Series(score_dict,index=score_dict.keys())
        return ds