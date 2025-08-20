'''
The main library for the score aggregator. Contains the ScoreLoader class, which is responsible for loading scores, doing so in a timed manner, and saving scores to files.
'''

from mlb_scores import GetScoresOnDay as _getMLBScores
from nba_scores import GetScores as _getNBAScores
from nfl_scores import GetScores as _getNFLScores
from scorecard import Scorecard

from datetime import date
from time import time, sleep

try:
    from pandas import DataFrame
    pd_enabled = True
except ModuleNotFoundError | ImportError as e:
    pd_exception = e
    pd_enabled = False

import json

class LoadError(LookupError):
    pass

class ScoreLoader:
    def __init__(self) -> None:
        self.mlb_scores = {}
        self.nba_scores = {}
        self.nfl_scores = {}

        self.requests_per_minute = 20
        self.last_mlb_load_time = 0
        self.last_nba_load_time = 0
        self.last_nfl_load_time = 0

        self.loaded_scores = {}

    def _timeSinceMLBLastLoad(self) -> float:
        return time() - self.last_mlb_load_time
    
    def _timeSinceNBALastLoad(self) -> float:
        return time() - self.last_nba_load_time
    
    def _timeSinceNFLLastLoad(self) -> float:
        return time() - self.last_nfl_load_time

    def GetMLBScores(self, day: date, default: bool = False) -> list[Scorecard]:
        if not (default or isinstance(day,date)):
            raise TypeError('Expected datetime.date object')

        if self._timeSinceMLBLastLoad() < self.requests_per_minute / 60:
            try:
                if default:
                    return self.mlb_scores[0]
                else:
                    return self.mlb_scores[day]
            except KeyError:
                wait_time = self.requests_per_minute / 60 - self._timeSinceMLBLastLoad()
                sleep(wait_time)
                scores =  _getMLBScores(day,default)
                if default:
                    self.mlb_scores[0] = scores
                else:
                    self.mlb_scores[day] = scores
                self.last_mlb_load_time = time()
                return scores
        else:
            scores =  _getMLBScores(day,default)
            if default:
                self.mlb_scores[0] = scores
            else:
                self.mlb_scores[day] = scores
            self.last_mlb_load_time = time()
            return scores

    def GetNFLScores(self, day: date, default: bool = False) -> list[Scorecard]:
        if not (default or isinstance(day,date)):
            raise TypeError('Expected datetime.date object')

        if self._timeSinceNFLLastLoad() < self.requests_per_minute / 60:
            try:
                if default:
                    return self.nfl_scores[0]
                else:
                    return self.nfl_scores[day]
            except KeyError:
                wait_time = self.requests_per_minute / 60 - self._timeSinceNFLLastLoad()
                sleep(wait_time)
                scores =  _getNFLScores(day,default=default)
                if default:
                    self.nfl_scores[0] = scores
                else:
                    self.nfl_scores[day] = scores
                self.last_nfl_load_time = time()
                return scores
        else:
            scores =  _getNFLScores(day,default=default)
            if default:
                self.nfl_scores[0] = scores
            else:
                self.nfl_scores[day] = scores
            self.last_nfl_load_time = time()
            return scores        

    def GetNBAScores(self, day: date, default: bool = False) -> list[Scorecard]:
        if not (default or isinstance(day,date)):
            raise TypeError('Expected datetime.date object')

        if self._timeSinceNBALastLoad() < self.requests_per_minute / 60:
            try:
                if default:
                    return self.nba_scores[0]
                else:
                    return self.nba_scores[day]
            except KeyError:
                wait_time = self.requests_per_minute / 60 - self._timeSinceNBALastLoad()
                sleep(wait_time)
                scores =  _getNBAScores(day,default)
                if default:
                    self.nba_scores[0] = scores
                else:
                    self.nba_scores[day] = scores
                self.last_nba_load_time = time()
                return scores
        else:
            scores =  _getNBAScores(day,default)
            if default:
                self.nba_scores[0] = scores
            else:
                self.nba_scores[day] = scores
            self.last_nba_load_time = time()
            return scores
        
    def LoadAllScores(self, day: date, default: bool = False) -> dict:
        if not (default or isinstance(day,date)):
            raise TypeError('Expected datetime.date object')

        scoreboard = {
            'scores' : {
                'mlb' : self.GetMLBScores(day,default),
                'nba' : self.GetNBAScores(day,default),
                'nfl' : self.GetNFLScores(day,default)
            },
            'date' : day
        }

        self.loaded_scores = scoreboard
        return scoreboard
    
    def GetScoreDataframe(self) -> DataFrame:
        if len(self.loaded_scores) <= 0:
            raise LoadError('No loaded scores')
        
        ds_list = []
        for league, scores in self.loaded_scores['scores'].items():
            for score in scores:
                if not isinstance(score, Scorecard):
                    continue
                score_ds = score.getSeries()
                score_ds['league'] = str.upper(league)
                ds_list.append(score_ds)
        
        if pd_enabled:
            df = DataFrame(ds_list)
            return df
        raise pd_exception

    def DumpLoadedScores(self, indent: int = 0) -> str:
        if len(self.loaded_scores) <= 0:
            raise LoadError('No loaded scores')
        
        dump_scoreboard = {
            'scores' : {
                'mlb' : [],
                'nba' : [],
                'nfl' : []
            },
            'date' : str(self.loaded_scores['date'])
        }

        for league, scores in self.loaded_scores['scores'].items():
            for score in scores:
                if not isinstance(score, Scorecard):
                    continue
                dump_scoreboard['scores'][league].append(score.getDict())

        dump = json.dumps(dump_scoreboard,indent=indent)

        return dump
    
    def DumpToFile(self, filename: str) -> None:
        dump = self.DumpLoadedScores(indent=4)

        with open(filename,'w') as file:
            file.write(dump)

