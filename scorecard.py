class Scorecard:
    def __init__(self):
        self.name_team1 = None
        self.name_team2 = None
        self.score_team1 = None
        self.score_team2 = None
        self.game_state = None

    def __repr__(self):
        score_str = ""
        score_str += f'{self.name_team1} @ {self.name_team2}'
        if not (self.score_team1 is None or self.score_team2 is None):
            score_str += f'\n{self.score_team1}-{self.score_team2}'
        score_str += f'\n{self.game_state}'
        return score_str

    def setNames(self,name_team1,name_team2):
        self.name_team1 = name_team1
        self.name_team2 = name_team2

    def setScore(self,score_team1,score_team2):
        self.score_team1 = score_team1
        self.score_team2 = score_team2

    def setState(self,state):
        self.game_state = state

    def asdict(self):
        return {
            'name_team1' : self.name_team1,
            'name_team2' : self.name_team2,
            'score_team1' : self.score_team1,
            'score_team2' : self.score_team2,
            'game_state' : self.game_state
        }
    
    