# import all assisting built in modules
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter
import json
import requests

# import all custom modules for parsing
from CSV_Writer import *

# import all custom modules for statistical analysis


team_codes = {
    'Anaheim Ducks' : 24,
    'Arizona Coyotes' : 53,
    'Boston Bruins' : 6,
    'Buffalo Sabres' : 7,
    'Calgary Flames' : 20,
    'Carolina Hurricanes' : 12,
    'Chicago Blackhawks' : 16,
    'Colorado Avalanche' : 21,
    'Columbus Blue Jackets' : 29,
    'Dallas Stars' : 25,
    'Detroit Red Wings' : 17,
    'Edmonton Oilers' : 22,
    'Florida Panthers' : 13,
    'Los Angeles Kings' : 26,
    'Minnesota Wild' : 30,
    'Montréal Canadiens' : 8,
    'Nashville Predators' : 18,
    'New Jersey Devils' : 1,
    'New York Islanders' : 2,
    'New York Rangers' : 3,
    'Ottawa Senators' : 9,
    'Philadelphia Flyers' : 4,
    'Pittsburgh Penguins' : 5,
    'San Jose Sharks' : 28,
    'Seattle Kraken' : 55,
    'St. Louis Blues' : 19,
    'Tampa Bay Lightning' : 14,
    'Toronto Maple Leafs' : 10,
    'Vancouver Canucks' : 23,
    'Vegas Golden Knights' : 54,
    'Washington Capitals' : 15,
    'Winnipeg Jets' : 52,
}

active_players = {
    'Center':{},
    'Right Wing':{},
    'Left Wing':{},
    'Defenseman':{},
    'Goalie':{}
}

def player_sorting() -> None:

    # loop through each team
    for team in team_codes.keys():
        roster_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.roster".format(team_codes[team])
        web_data = requests.get(roster_url)
        parsed_data = json.loads(web_data.content)

        # for each listed player in the roster, store the name as the key
        # and the ID as the value so they can be individually searched later
        print(team)
        for player in parsed_data["teams"][0]["roster"]["roster"]:
            active_players[player["position"]["name"]] \
                [player["person"]["fullName"]] = player["person"]["id"]

            if team == 'Anaheim Ducks':
                print(active_players)

if __name__ == "__main__":
    player_sorting()
