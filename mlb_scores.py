import requests
import warnings
from bs4 import BeautifulSoup, Tag
from datetime import date
from scorecard import Scorecard

_score_url = "https://www.mlb.com/scores/"

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

def ContainerIsEmpty(soup):
    if not (isinstance(soup,BeautifulSoup) or isinstance(soup,Tag)):
        raise TypeError('Expected BeautifulSoup or Tag object')
    EmptyCollectionDiv = soup.find('div',class_ = 'EmptyCollectionstyle__EmptyWrapper-sc-4fquet-0 hAoHOT')
    if EmptyCollectionDiv is None:
        return False
    return True

def GetScorecardFromElement(element,day):
    if not (isinstance(element,BeautifulSoup) or isinstance(element,Tag)):
        raise TypeError('Expected BeautifulSoup or Tag object')
    
    state_element = element.find('div',class_ = 'StatusLayerstyle__StatusLayerValue-sc-1s2c2o8-2')
    team_name_elements = element.find_all('div',class_ = 'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0 fdaoCu')
    team_abbr_elements = element.find_all('div',class_ = 'TeamWrappersstyle__MobileTeamWrapper-sc-uqs6qh-1 jXnGyx')
    scoreboard_element = element.find('table',class_ = 'tablestyle__StyledTable-sc-wsl6eq-0 fxhlOg')

    state = None
    if state_element is not None:
        state = str.split(state_element.text,'\u00a0')[0]

    team_names = [x.text for x in team_name_elements]
    team_abbrs = [x.text for x in team_abbr_elements]

    try:
        scoreboard_rows = scoreboard_element.find('tbody').find_all('tr')
        scores = [int(row.find('td').text) for row in scoreboard_rows]
    except AttributeError:
        scores = [None,None]
    except ValueError:
        scores = [None,None]

    scorecard = Scorecard()
    scorecard.setState(state)
    scorecard.setNames(team_names[0],team_names[1])
    scorecard.setAbbrs(team_abbrs[0],team_abbrs[1])
    scorecard.setScore(scores[0],scores[1])
    scorecard.setDate(day)

    return scorecard

def GetScores(day):
    soup = GetSoup(day)
    if soup is None:
        warnings.warn('MLB scores site did not properly load')
        return []
    
    gameContainer = soup.find('section',class_ = 'SnSstyle__GameCardsWrapper-sc-1m2zl7j-0')
    if gameContainer is None:
        warnings.warn('Score container could not be found')
        return []

    no_scores = ContainerIsEmpty(gameContainer)
    if no_scores:
        return []
    
    scorecard_elements = gameContainer.find_all('div',class_ = 'ScoresGamestyle__ExpandedScoresGameWrapper-sc-7t80if-0 ScoresGamestyle__DesktopScoresGameWrapper-sc-7t80if-1 gPLsYH')
    scorecards = [GetScorecardFromElement(element,day) for element in scorecard_elements]

    scores = sorted(scorecards)

    return scores

def main():
    today = date.today()
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()