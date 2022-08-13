import requests
import json
from numpy import std, var

records_url = \
    'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
web_data = requests.get(records_url)
special_teams_data = {}
parsed_data = json.loads(web_data.content)
win_score_first = []
for team in parsed_data["teams"]:
    win_score_first.append(
        team["teamStats"][0]["splits"][0]["stat"]['winScoreFirst'])
        
print(std(win_score_first))
print(var(win_score_first))
