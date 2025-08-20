"""
Library that enables the collection of NFL score info from https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard/ and returns it as a list of scorecard objects.
Information collected via the ESPN NFL scoreboard API

Note that when calling GetScores() for a specific date, the scores returned will be from the week that that day is in.

Scores accessible from the 2000 NFL season onward.
"""

import requests
from datetime import date, timedelta
from scorecard import Scorecard
from nfl_week import FindNearestWeek

def ProcessCompetition(competition: dict) -> Scorecard:
    competitors = competition['competitors']
    status = competition['status']
    date_raw = competition['startDate']

    # Construct time

    date_raw_parts = str.split(date_raw,'T')
    
    time_raw = str.replace(date_raw_parts[1],"Z","")
    clock_parts = [int(num) for num in str.split(time_raw,':')]
    date_lowered = clock_parts[0] < 4

    hour = (clock_parts[0] - 4) % 24
    minute = clock_parts[1]

    time_text = ''
    if hour > 12:
        time_text = f"{(hour - 12):02d}:{minute:02d} pm ET"
    elif hour == 12:
        time_text = f"12:{minute:02d} pm ET"
    elif hour == 0:
        time_text = f"12:{minute:02d} am ET"
    else:
        time_text = f"{hour:02d}:{minute:02d} am ET"
    
    # Construct date

    date_raw = date_raw_parts[0]
    day_parts = [int(num) for num in str.split(date_raw,'-')]
    game_date = date(day_parts[0],day_parts[1],day_parts[2])
    if date_lowered:
        d = timedelta(days=1)
        game_date -= d
    

    # Construct status

    status_type = status['type']
    status_name = status_type['name']
    game_started = False
    if status_type['id'] != "1":
        game_started = True

    status_text = ""
    quarter = status['period']
    if not game_started:
        status_text = time_text
    elif status_type['id'] == "2" and status_name == 'STATUS_HALFTIME':
        status_text = 'Halftime'
    elif status_type['id'] == "2":
        display_clock = status['displayClock']
        status_text = f'Q{quarter} {display_clock}'
    elif status_type['id'] == "22":
        status_text = f"END Q{quarter}"
    else:
        status_text = status['type']['detail']

    # Team info

    home_team = {}
    away_team = {}

    for competitor in competitors:
        team_name = competitor['team']['name']
        team_abbr = competitor['team']['abbreviation']
        team_score = int(competitor['score'])
        if competitor['homeAway'] == 'home':
            home_team['name'] = team_name
            home_team['abbr'] = team_abbr
            home_team['score'] = team_score
        else:
            away_team['name'] = team_name
            away_team['abbr'] = team_abbr
            away_team['score'] = team_score

    # Construct and return scorecard

    score = Scorecard()
    score.setDate(game_date)
    score.setState(status_text)
    score.setNames(away_team['name'],home_team['name'])
    score.setAbbrs(away_team['abbr'],home_team['abbr'])
    if game_started:
        score.setScore(away_team['score'],home_team['score'])
    
    return score

def ProcessEvents(events: list) -> list[Scorecard]:
    scores = []
    for event in events:
        competitions = event['competitions']
        event_scores = [ProcessCompetition(competition) for competition in competitions]
        scores += event_scores

    return scores

def GetScores(day: date, default: bool = False) -> list[Scorecard]:
    scores = None
    base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'

    if day == date.today() or default:
        r = requests.get(base_url)
        if r.status_code != 200:
            r.raise_for_status()

        data = r.json()

        events = data['events']
        scores = ProcessEvents(events)
    else:
        week = FindNearestWeek(day)
        if week is None:
            return []
        season = week.season
        week_num = week.week_num
        season_type = week.week_type.value

        url = f'{base_url}?dates={season}&seasontype={season_type}&week={week_num}'

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        data = r.json()

        events = data['events']
        scores = ProcessEvents(events)

    return scores

def main() -> None:
    today = date.today()
    scores = GetScores(today)
    for score in scores:
        print(score,end='\n\n')

if __name__ == "__main__":
    main()
