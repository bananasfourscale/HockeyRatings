# import all assisting built in modules
import json
import requests

# import all custom modules for parsing
from CSV_Writer import write_out_player_file

# import all custom modules for statistical analysis
from Goalie_Metrics.Goalie_Utilization import goalie_utilization_get_dict, \
    goalie_utilization_calculate_time_on_ice
from Goalie_Metrics.Goalie_Win_Rating import goalie_win_rating_get_dict, \
    goalie_win_rating_calculate
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
        for player in parsed_data["teams"][0]["roster"]["roster"]:
            active_players[player["position"]["name"]] \
                [player["person"]["fullName"]] = \
                    [player["person"]["id"], parsed_data["teams"][0]["name"]]


def goalie_utilization() -> None:
    goalie_utilization_calculate_time_on_ice(active_players['Goalie'],
        team_codes)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization", "Team"], goalie_utilization_get_dict(),
        active_players['Goalie'])
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization"],
        max(list(goalie_utilization_get_dict().values())),
        min(list(goalie_utilization_get_dict().values())), [],
        "Graphs/Goalies/Utilization/utilization_base.png")

    # apply correction
    goalie_utilization = apply_sigmoid_correction(
        goalie_utilization_get_dict())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization", "Team"], goalie_utilization,
        active_players['Goalie'])
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Utilization.csv",
        ["Goalie", "Utilization"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Goalies/Utilization/utilization_corrected.png")


def goalie_win_rating() -> None:
    goalie_win_rating_calculate(active_players['Goalie'], team_codes)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating.csv",
        ["Goalie", "Win Rating", "Team"], goalie_win_rating_get_dict(),
        active_players['Goalie'])
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating.csv",
        ["Goalie", "Win Rating"],
        max(list(goalie_win_rating_get_dict().values())),
        min(list(goalie_win_rating_get_dict().values())), [],
        "Graphs/Goalies/Win_Rating/win_rating_base.png")

    # apply correction
    goalie_win_rating = apply_sigmoid_correction(
        goalie_win_rating_get_dict())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating.csv",
        ["Goalie", "Win Rating", "Team"], goalie_win_rating,
        active_players['Goalie'])
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating.csv",
        ["Goalie", "Win Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Goalies/Win_Rating/win_rating_corrected.png")


def calculate_goalie_metrics() -> None:
    goalie_utilization()
    goalie_win_rating()
    


if __name__ == "__main__":

    # get all players and sort them into the list for their position
    player_sorting()
    calculate_goalie_metrics()
