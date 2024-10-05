# Scrapes NBA scores from https://www.nba.come/games and returns them as a list of scorecard objects
# Finds json of score data and parses it for informations

import requests
import warnings
import json
from bs4 import BeautifulSoup, Tag
from datetime import date
from scorecard import Scorecard

_score_url = 'https://www.nba.com/games?date='

def GetScoreUrl(day,default = False):
    if default:
        return 'https://www.nba.com/games'
    
    if not isinstance(day,date):
        raise TypeError('Expected Date object')
    return _score_url + str(day)

def GetSite(day,default = False):
    score_url = GetScoreUrl(day,default)
    data = requests.get(score_url)
    if data.status_code != 200:
        data.raise_for_status()
    return data

def GetSoup(day,default = False):
    scores_site = GetSite(day,default)
    if scores_site is None:
        return None
    return BeautifulSoup(scores_site.text,'html.parser')

def FindScoreScript(soup):
    if not isinstance(soup,BeautifulSoup):
        raise TypeError('Expected BeautifulSoup object')
    scripts = soup.find_all('script')
    for script in scripts:
        if script.get('id') == '__NEXT_DATA__':
            script_text =  script.text
            script_details = json.loads(script_text)
            return script_details
    return None

def NoScores(scorecard_json):
    modules = scorecard_json['props']['pageProps']['gameCardFeed']['modules']
    if len(modules) > 0:
        return False
    return True

def ProcessCard(card,day):
    data = card['cardData']
    home_team = data['homeTeam']
    away_team = data['awayTeam']
    status_num = data['gameStatus']

    state = data['gameStatusText']
    team_names = [away_team['teamName'],home_team['teamName']]
    team_abbrs = [away_team['teamTricode'],home_team['teamTricode']]
    if status_num == 1:
        scores = [None,None]
    else:
        scores = [away_team['score'],home_team['score']]

    scorecard = Scorecard()
    scorecard.setState(state)
    scorecard.setNames(team_names[0],team_names[1])
    scorecard.setAbbrs(team_abbrs[0],team_abbrs[1])
    scorecard.setScore(scores[0],scores[1])
    try:
        scorecard.setDate(day)
    except TypeError:
        pass

    return scorecard

def GetScores(day,default = False):
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

    scorecards = [ProcessCard(card,day) for card in cards]

    scores = sorted(scorecards)

    return scores
    
def main():
    today = date(1969,4,20)
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()