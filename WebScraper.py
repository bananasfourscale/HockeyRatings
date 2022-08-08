import requests
import json

records_url = \
    'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
web_data = requests.get(records_url)
special_teams_data = {}
parsed_data = json.loads(web_data.content)
for team in parsed_data["teams"]:
    PPper = team["teamStats"][0]["splits"][0]["stat"]
    print(PPper)
