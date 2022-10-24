# import all assisting built in modules
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter
import json
import requests

# import all custom modules for parsing
from CSV_Writer import write_out_player_file

# import all custom modules for statistical analysis
from Goalie_Metrics.Goalie_List import populate_active_goalies, \
    get_active_goalies
from Goalie_Metrics.Goalie_Utilization import get_goalie_utilization_ranking, \
    get_time_on_ice
from Sigmoid_Correction import apply_sigmoid_correction
from Plotter import plot_player_ranking


sigmiod_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


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
    populate_active_goalies()
    get_time_on_ice()
    goalie_utilization = apply_sigmoid_correction(
        get_goalie_utilization_ranking())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization", "Team"], goalie_utilization,
        get_active_goalies())
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Goalies/Utilization/utilization_corrected.png")
