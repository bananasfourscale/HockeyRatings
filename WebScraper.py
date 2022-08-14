import requests
import json
from numpy import std, var


# Get the top level record from the API
records_url = \
    "https://statsapi.web.nhl.com/api/v1/schedule?season=20212022&gameType=R" + \
        "&expand=schedule.linescore"
web_data = requests.get(records_url)
parsed_data = json.loads(web_data.content)

# place match data in a dict of list of games for later use
match_data = {}

# matches are orginized by date they take place
for date in parsed_data["dates"]:
    game_data = []

    # for each game on a specific date loop through
    for game in date["games"]:

        # if the game is a completed regular season game then add to list
        if (game["status"]["abstractGameState"] == "Final"):
            away_name = game["teams"]["away"]["team"]["name"]
            away_score = game["teams"]["away"]["score"]
            home_name = game["teams"]["home"]["team"]["name"]
            home_score = game["teams"]["home"]["score"]
            game_end_type = game["linescore"]["currentPeriodOrdinal"]
            game_data.append([away_name, away_score, home_name, home_score,
                game_end_type])
    match_data[date["date"]] = game_data

with open("test_file.txt", "w") as test_file:
    for date in match_data.keys():
        test_file.writelines(date + str(match_data[date]))
