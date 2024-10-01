from datetime import date

class Scorecard:
    def __init__(self):
        self.name_team1 = None
        self.name_team2 = None
        self.score_team1 = None
        self.score_team2 = None
        self.game_state = None
        self.date = None

    def __repr__(self):
        score_str = ""

        if self.score_team1 is not None and self.score_team2 is not None and self.name_team1 is not None and self.name_team2 is not None:
            score_str += "{:<30}{:>3}\n".format(self.name_team1,self.score_team1)
            score_str += "{:<30}{:>3}".format(self.name_team2,self.score_team2)
        elif self.name_team1 is not None and self.name_team2 is not None:
            score_str += f'{self.name_team1}\n{self.name_team2}'

        footer_added = False
        if self.game_state is not None:
            score_str += f'\n{self.game_state}'
            footer_added = True
        if self.date is not None:
            if not footer_added:
                score_str += '\n'
            else:
                score_str += ' '
            score_str += f'({str(self.date)})'

        return score_str

    def setNames(self,name_team1,name_team2):
        self.name_team1 = name_team1
        self.name_team2 = name_team2

    def setScore(self,score_team1,score_team2):
        self.score_team1 = score_team1
        self.score_team2 = score_team2

    def setState(self,state):
        self.game_state = state

    def setDate(self,day):
        if not isinstance(day,date):
            raise TypeError('Expected date object')
        self.date = day

    def asdict(self):
        return {
            'name_team1' : self.name_team1,
            'name_team2' : self.name_team2,
            'score_team1' : self.score_team1,
            'score_team2' : self.score_team2,
            'game_state' : self.game_state
        }
    
    