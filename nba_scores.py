"""
Library that enables the collection of NBA score info from https://www.nba.com/games and returns it as a list of scorecard objects.
Information collected via data contained in the __NEXT_DATA__ script on the scores page.

Scores accessible from the 1946-47 BAA season onward. (Does not contain data for the ABA)
"""

import requests
import warnings
import json
from bs4 import BeautifulSoup, Tag
from datetime import date
from scorecard import Scorecard

_score_url = 'https://www.nba.com/games?date='

def GetScoreUrl(day: date, default = False) -> str:
    if default:
        return 'https://www.nba.com/games'
    return _score_url + str(day)

def GetSite(day: date, default: bool = False) -> requests.Response:
    score_url = GetScoreUrl(day, default)
    data = requests.get(score_url)
    if data.status_code != 200:
        data.raise_for_status()
    return data

def GetSoup(day: date, default: bool = False) -> BeautifulSoup:
    scores_site = GetSite(day,default)
    if scores_site is None:
        return None
    return BeautifulSoup(scores_site.text,'html.parser')

def FindScoreScript(soup: BeautifulSoup) -> (dict | None):
    if not isinstance(soup,BeautifulSoup):
        raise TypeError('Expected BeautifulSoup object')
    scripts = soup.find_all('script')
    for script in scripts:
        if script.get('id') == '__NEXT_DATA__':
            script_text =  script.text
            script_details = json.loads(script_text)
            return script_details
    return None

def NoScores(scorecard_json: dict) -> bool:
    modules = scorecard_json['props']['pageProps']['gameCardFeed']['modules']
    if len(modules) > 0:
        return False
    return True

def ProcessCard(card: dict) -> Scorecard:
    data = card['cardData']
    home_team = data['homeTeam']
    away_team = data['awayTeam']
    status_num = data['gameStatus']
    game_time = data['gameTimeEastern']

    if home_team is None:
        home_team = dict()
        home_team['teamName'] = 'TBA'
        home_team['teamTricode'] = 'TBA'
        home_team['score'] = 0
    if away_team is None:
        away_team = dict()
        away_team['teamName'] = 'TBA'
        away_team['teamTricode'] = 'TBA'
        away_team['score'] = 0

    state = data['gameStatusText']
    team_names = [away_team['teamName'],home_team['teamName']]
    team_abbrs = [away_team['teamTricode'],home_team['teamTricode']]
    if status_num == 1:
        scores = [None,None]
    else:
        scores = [away_team['score'],home_team['score']]

    date_text = str.split(game_time,'T')[0]
    date_parts = [int(part) for part in str.split(date_text,'-')]

    scorecard = Scorecard()
    scorecard.setState(state)
    scorecard.setNames(team_names[0],team_names[1])
    scorecard.setAbbrs(team_abbrs[0],team_abbrs[1])
    scorecard.setScore(scores[0],scores[1])
    scorecard.setDate(date(date_parts[0],date_parts[1],date_parts[2]))

    return scorecard

def GetScores(day: date, default: bool = False) -> list[Scorecard]:
    soup = GetSoup(day,default)
    if soup is None:
        warnings.warn('NBA scores site did not properly load')
        return []
    
    scorecard_json = FindScoreScript(soup)
    if scorecard_json is None:
        warnings.warn('Could not load score json')
        return []
    
    if NoScores(scorecard_json):
        return []

    cards = scorecard_json['props']['pageProps']['gameCardFeed']['modules'][0]['cards']

    scorecards = [ProcessCard(card) for card in cards]

    scores = sorted(scorecards)

    return scores
    
def main() -> None:
    today = date.today()
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()