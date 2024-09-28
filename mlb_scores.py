from bs4 import BeautifulSoup
import requests
from dates import Date

_score_url = "https://www.mlb.com/scores/"

def GetScoreUrl(day):
    if not isinstance(day,Date):
        raise TypeError('Expected Date object')
    return _score_url + day.mlb_str()

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

def GetScores(day):
    soup = GetSoup(day)
    gameContainer = soup.find('section',class_ = 'SnSstyle__GameCardsWrapper-sc-1m2zl7j-0 fZsilK')
    print(gameContainer)

def main():
    today = Date()
    today.SetToday()
    GetScores(today)

if __name__ == '__main__':
    main()