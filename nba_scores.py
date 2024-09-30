import requests
import warnings
import json
from bs4 import BeautifulSoup, Tag
from datetime import date
from scorecard import Scorecard

_score_url = 'https://www.nba.com/games?date='

def GetScoreUrl(day):
    if not isinstance(day,date):
        raise TypeError('Expected Date object')
    return _score_url + str(day)

def GetSite(day):
    score_url = GetScoreUrl(day)
    data = requests.get(score_url)
    if data.status_code != 200:
        data.raise_for_status()
    return data

def GetSoup(day):
    scores_site = GetSite(day)
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
    if status_num == 1:
        scores = [None,None]
    else:
        scores = [away_team['score'],home_team['score']]

    scorecard = Scorecard()
    scorecard.setState(state)
    scorecard.setNames(team_names[0],team_names[1])
    scorecard.setScore(scores[0],scores[1])
    scorecard.setDate(day)

    return scorecard

def GetScores(day):
    soup = GetSoup(day)
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

    return scorecards
    
def main():
    today = date(1969,4,20)
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()