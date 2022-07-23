import requests
import json
url1 = 'https://statsapi.web.nhl.com/api/v1/teams'

if __name__ == "__main__":
    data = requests.get(url1)
    parsed_data = json.loads(data.content)
    for team in parsed_data["teams"]:
        print("team: {} = {}".format(team["name"], team["id"]))
