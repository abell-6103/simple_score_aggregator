# Scrapes NFL scores from https://www.sports.yahoo.com/nfl/scoreboard and returns them as a list of scorecard objects
# Finds json of score data and parses it for information

import requests
import warnings
import json
from bs4 import BeautifulSoup, Tag
from datetime import date
from scorecard import Scorecard
import nfl_week as weeks

def GetYahooUrl(week):
    if not isinstance(week,weeks.NFLWeek):
        raise TypeError('Expected NFLWeek object')
    
    week_num = week.week_num
    season = week.season
    season_type = week.week_type.value

    return f'https://sports.yahoo.com/nfl/scoreboard/?confId=&dateRange={week_num}&schedState={season_type}&scoreboardSeason={season}'

def GetScoreUrl(day,year_override = False,default = False):
    if default:
        return 'https://sports.yahoo.com/nfl/scoreboard/'
    
    if not isinstance(day,date):
        raise TypeError('Expected Date object')
    week = weeks.FindNearestWeek(day,year_override)
    if week is None:
        return None
    return GetYahooUrl(week)

def GetSite(day,year_override = False,default = False):
    score_url = GetScoreUrl(day,year_override,default)
    if score_url is None:
        return None
    data = requests.get(score_url)
    if data.status_code != 200:
        data.raise_for_status()
    return data

def GetSoup(day,year_override = False,default = False):
    scores_site = GetSite(day,year_override,default)
    if scores_site is None:
        return None
    return BeautifulSoup(scores_site.text,'html.parser')

def ContainerIsEmpty(soup):
    if not (isinstance(soup,BeautifulSoup) or isinstance(soup,Tag)):
        raise TypeError('Expected BeautifulSoup or Tag object')
    span = soup.find('span')
    if span is None:
        return False
    span_text = span.text[0:8]
    if span_text == 'No games':
        return True
    return False

def GetData(soup):
    if not isinstance(soup,BeautifulSoup):
        raise TypeError('Expected BeautifulSoup object')
    
    scripts = soup.find_all('script')
    script = None

    for i_script in scripts:
        if str.find(i_script.text,'/* -- Data -- */') != -1:
            script = i_script

    if script is None:
        return None
    
    script_text = script.text
    split_1 = str.split(script_text,'root.App.main = ')
    if len(split_1) == 1:
        return None
    split_2 = str.split(split_1[1],';\n')
    if len(split_2) == 1:
        return None
    
    json_text = split_2[0]
    details = json.loads(json_text)

    return details

def GetTeamDict(TeamsStore,week,default = False):
    teams = {}

    if isinstance(week,weeks.NFLWeek):
        season = week.season
    elif not default:
        raise TypeError('Expected NFLWeek object')

    teams_data = TeamsStore['teams']
    for team_id in teams_data:
        if str.find(team_id,'nfl.t') == -1:
            continue
        team_data = teams_data[team_id]
        last_name = team_data['last_name']
        abbr = team_data['abbr']

        if not default:
            if last_name == 'Commanders' and season < 2020:
                last_name = 'Redskins'
            elif last_name == 'Commanders' and season < 2022:
                last_name = 'Washington Football Team'

            if abbr == 'LV' and season < 2020:
                abbr = 'OAK'
            
            if abbr == 'LA' and season < 2016:
                abbr = 'STL'

            if abbr == 'LAC' and season < 2017:
                abbr = 'SD'

        teams[team_id] = [last_name,abbr]

    return teams

def GetScorecards(GamesStore,TeamsDict,week,default = False):
    games = GamesStore['games']
    
    scorecards = []
    for game_tag in games:
        if str.find(game_tag,'nfl.g') == -1:
            continue
        
        game_date_str = (str.split(game_tag,'.')[2])[0:8]
        game_day = date(int(game_date_str[0:4]),int(game_date_str[4:6]),int(game_date_str[6:8]))
        if (not default) and (weeks.FindNearestWeek(game_day) != week):
            continue

        game = games[game_tag]

        team1_name = TeamsDict[game['away_team_id']][0]
        team2_name = TeamsDict[game['home_team_id']][0]

        team1_abbr = TeamsDict[game['away_team_id']][1]
        team2_abbr = TeamsDict[game['home_team_id']][1]

        team1_score = game['total_away_points']
        team2_score = game['total_home_points']

        game_status = game['status_display_name']

        scorecard = Scorecard()
        scorecard.setNames(team1_name,team2_name)
        scorecard.setAbbrs(team1_abbr,team2_abbr)
        scorecard.setScore(team1_score,team2_score)
        scorecard.setState(game_status)
        scorecard.setDate(game_day)

        scorecards.append(scorecard)
    
    return scorecards


def GetScores(day,year_override = False,default = False):
    if not default:
        try:
            week = weeks.FindNearestWeek(day)
        except ValueError:
            return []
        
        if week is None:
            return []
    else:
        week = None

    soup = GetSoup(day,year_override,default)
    if soup is None:
        warnings.warn('NFL scores site did not properly load')
        return []
    
    gameContainer = soup.find('div',{'id' : 'scoreboard-group-2'})
    if gameContainer is None:
        warnings.warn('Score container could not be found')
        return []
    
    no_scores = ContainerIsEmpty(gameContainer)
    if no_scores:
        return []
    
    data = GetData(soup)
    if data is None:
        warnings.warn('Could not load data script')
        return []
    
    TeamsStore = data['context']['dispatcher']['stores']['TeamsStore']
    TeamsDict = GetTeamDict(TeamsStore,week,default)

    if len(TeamsDict) < 1:
        warnings.warn('Could not load teams')
        return []

    GamesStore = data['context']['dispatcher']['stores']['GamesStore']
    scorecards = GetScorecards(GamesStore,TeamsDict,week,default)
    
    scores = sorted(scorecards,key= lambda x: x.date)

    return scores
    
def main():
    today = date.today()
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()