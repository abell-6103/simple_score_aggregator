"""
Library that enables the collection of MLB score info from https://statsapi.mlb.com/api/ and returns it as a list of scorecard objects.
Information collected via MLB's official stats api.

Scores accessible from the 1901 MLB season onward, though older team names may not be accurate.
"""

import requests
from datetime import date
from scorecard import Scorecard

def GetScoreUrl(startDate: date, endDate: date, default: bool = False) -> str:
    if startDate is None and endDate is None:
        default = True

    if default:
        return 'https://statsapi.mlb.com/api/v1/schedule?sportId=1'
    
    return f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={str(startDate)}&endDate={str(endDate)}'

def LoadScoreJson(startDate: date, endDate: date, default: bool = False) -> dict:
    url = GetScoreUrl(startDate,endDate,default)
    r = requests.get(url)
    if r.status_code != 200:
        raise requests.HTTPError('Failed to load scores')
    return r.json()

def LoadTeams() -> dict:
    r = requests.get('https://statsapi.mlb.com/api/v1/teams?sportId=1')
    if r.status_code != 200:
        raise requests.HTTPError('Failed to load teams')
    teams_json = r.json()
    teams_list = teams_json['teams']

    teams = {}

    for team in teams_list:
        id = team['id']
        try:
            name = team['clubName']
        except KeyError:
            name = team['teamName']
        abbr = team['abbreviation']
        teams[id] = name, abbr

    return teams

def ConvertToScorecard(game: dict, team_dict: dict, ignoreLive: bool = True) -> Scorecard:
    teams = game['teams']

    away_team = teams['away']
    away_id = away_team['team']['id']
    try:
        away_name, away_abbr = team_dict[away_id]
    except KeyError:
        away_name, away_abbr = 'TBD','TBD'

    try:
        away_score = away_team['score']
    except KeyError:
        away_score = None

    home_team = teams['home']
    home_id = home_team['team']['id']
    try:
        home_name, home_abbr = team_dict[home_id]
    except KeyError:
        home_name, home_abbr = 'TBD','TBD'

    try:
        home_score = home_team['score']
    except KeyError:
        home_score = None

    official_date_text = game['officialDate']
    official_date_parts = [int(part) for part in str.split(official_date_text,'-')]
    official_date = date(official_date_parts[0],official_date_parts[1],official_date_parts[2])

    game_date_text = game['gameDate']
    game_time_text = game_date_text[11:18]
    game_time_hour_raw = (int(str.split(game_time_text,':')[0]) - 4) % 24
    game_time_minute = int(str.split(game_time_text,':')[1])
    if game_time_hour_raw > 12:
        game_time = f'{game_time_hour_raw - 12}:{game_time_minute:02d} pm ET'
    elif game_time_hour_raw == 0:
        game_time = f'12:{game_time_minute:02d} am ET'
    else:
        game_time = f'{game_time_hour_raw}:{game_time_minute:02d} am ET'

    abstract_status = game['status']['abstractGameState']
    coded_state = game['status']['codedGameState']
    status_text = game['status']['detailedState']
    if game['status']['startTimeTBD'] and abstract_status == 'Preview':
        status_text = 'TBD'
    elif abstract_status == 'Preview':
        status_text = game_time
    elif abstract_status == 'Live' and not ignoreLive and coded_state != 'I':
        status_text += f' {game_time}'
    elif abstract_status == 'Live' and not ignoreLive and coded_state == 'I':
        base_link = 'https://statsapi.mlb.com'
        live_link = game['link']
        game_json = requests.get(f'{base_link}{live_link}').json()
        linescore = game_json['liveData']['linescore']
        status_text = f'{str.upper(linescore["inningState"][0:3])} {linescore["currentInning"]}'

    game_started = coded_state == 'I' or coded_state == 'F'

    card = Scorecard()
    card.setAbbrs(away_abbr,home_abbr)
    card.setNames(away_name,home_name)
    if game_started: card.setScore(away_score,home_score)
    card.setState(status_text)
    card.setDate(official_date)

    return card

def GetScores(startDate: date, endDate: date, default: bool = False, ignoreLive: bool = True) -> list[Scorecard]:
    score_json = LoadScoreJson(startDate,endDate,default)
    team_dict = LoadTeams()

    dates = score_json['dates']
    scorecards = []

    for date in dates:
        scores = [ConvertToScorecard(game,team_dict,ignoreLive) for game in date['games']]
        scorecards += scores

    return scorecards

def GetScoresOnDay(day: date, default: bool = False, ignoreLive: bool = False) -> list[Scorecard]:
    return GetScores(day,day,default,ignoreLive)

def main() -> None:
    today = date.today()
    scores = GetScoresOnDay(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == '__main__':
    main()
