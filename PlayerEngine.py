# import all assisting built in modules
import json
import requests
from multiprocessing import Process, Queue, freeze_support
import os
import time

# import all custom modules for parsing
from CSV_Writer import write_out_player_file
from Worker_Nodes import plotter_worker

# import all custom modules for statistical analysis
from Goalie_Metrics.Goalie_Utilization import goalie_utilization_get_dict, \
    goalie_utilization_calculate_time_on_ice
from Goalie_Metrics.Goalie_Win_Rating import goalie_win_rating_get_dict, \
    goalie_win_rating_calculate
from Goalie_Metrics.Goalie_Save_Percentage import \
    goalie_save_percentage_get_dict, goalie_save_percentage_get_data, \
    goalie_save_percentage_scale_for_volume, \
    goalie_save_percentage_combine_metrics
from Goalie_Metrics.Goalie_Goals_Against import goalie_goals_against_get_dict, \
    goalie_goals_against_get_data

from Defensemen_Metrics.Defensemen_Hits import defensemen_hits_get_dict, \
    defensemen_hits_get_data
from Defensemen_Metrics.Defensemen_Blocks import defensemen_blocks_get_dict, \
    defensemen_blocks_get_data
from Defensemen_Metrics.Defensemen_Utilization import \
    defensemen_utilization_get_dict, defensemen_utilization_get_data, \
    defensemen_utilization_combine_metrics
from Defensemen_Metrics.Defensemen_Discipline import \
    defensemen_discipline_get_dict, defensemen_discipline_get_data
from Defensemen_Metrics.Defensemen_PlusMinus import \
    defensemen_plus_minus_get_dict, defensemen_plus_minus_get_data
from Defensemen_Metrics.Defensemen_Points import defensemen_points_get_dict, \
    defensemen_points_get_data

from Forward_Metrics.Forward_Points import forward_points_get_dict, \
    forward_points_get_data
from Forward_Metrics.Forward_Utilization import forward_utilization_get_dict, \
    forward_utilization_get_data, forward_utilization_combine_metrics
from Forward_Metrics.Forward_PlusMinus import forward_plus_minus_get_dict, \
    forward_plus_minus_get_data

from Sigmoid_Correction import apply_sigmoid_correction
from Weights import goalie_rating_weights, defensemen_rating_weights, \
    forward_rating_weights
from Plotter import plot_player_ranking


sigmoid_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


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
    'Goalie':{},
    'Forwards':{},
}


team_stats = {
    'Anaheim Ducks' : {},
    'Arizona Coyotes' : {},
    'Boston Bruins' : {},
    'Buffalo Sabres' : {},
    'Calgary Flames' : {},
    'Carolina Hurricanes' : {},
    'Chicago Blackhawks' : {},
    'Colorado Avalanche' : {},
    'Columbus Blue Jackets' : {},
    'Dallas Stars' : {},
    'Detroit Red Wings' : {},
    'Edmonton Oilers' : {},
    'Florida Panthers' : {},
    'Los Angeles Kings' : {},
    'Minnesota Wild' : {},
    'Montréal Canadiens' : {},
    'Nashville Predators' : {},
    'New Jersey Devils' : {},
    'New York Islanders' : {},
    'New York Rangers' : {},
    'Ottawa Senators' : {},
    'Philadelphia Flyers' : {},
    'Pittsburgh Penguins' : {},
    'San Jose Sharks' : {},
    'Seattle Kraken' : {},
    'St. Louis Blues' : {},
    'Tampa Bay Lightning' : {},
    'Toronto Maple Leafs' : {},
    'Vancouver Canucks' : {},
    'Vegas Golden Knights' : {},
    'Washington Capitals' : {},
    'Winnipeg Jets' : {},
}


player_eng_plotting_queue = Queue()


def player_sorting() -> None:

    # loop through each team
    for team in team_codes.keys():
        roster_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.roster".format(team_codes[team])
        web_data = requests.get(roster_url)
        roster_data = json.loads(web_data.content)

        # for each listed player in the roster, store the name as the key
        # and the ID as the value so they can be individually searched later
        for player in roster_data["teams"][0]["roster"]["roster"]:

            # NOTE only to shorten time while testing
            #if player["position"]["name"] == 'Defenseman':
            player_url = "https://statsapi.web.nhl.com/api/v1/people/" + \
                "{}/stats?stats=statsSingleSeason&season=20222023".format(
                player["person"]["id"])
            web_data = requests.get(player_url)
            player_data = json.loads(web_data.content)

            # make sure the goalie has stats
            if len(player_data["stats"][0]["splits"]) > 0:

                # shortcut to access stats more cleanly
                player_stats = player_data["stats"][0]["splits"][0]["stat"]
                if player["position"]["name"] == 'Defenseman' or \
                    player["position"]["name"] == 'Goalie':

                    # these positions have their own dict
                    active_players[player["position"]["name"]] \
                        [player["person"]["fullName"]] = \
                        [player_stats, roster_data["teams"][0]["name"]]

                else:

                    # all forwards are currently grouped together
                    active_players["Forwards"][player["person"]["fullName"]] = \
                        [player_stats, roster_data["teams"][0]["name"]]


def get_team_stats() -> None:

    # Team lists are so small relative to the list of all player data, just get
    # the data and store it to save time looking it up over and over
    for team in team_codes.keys():
        team_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.stats".format(team_codes[team])
        team_web_data = requests.get(team_url)
        team_parsed_data = json.loads(team_web_data.content)
        team_stats[team] = \
            team_parsed_data["teams"][0]["teamStats"][0]["splits"][0]["stat"]


def goalie_utilization() -> None:
    goalie_utilization_calculate_time_on_ice(active_players['Goalie'],
        team_stats)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Base.csv",
        ["Goalie", "Utilization Base", "Team"], goalie_utilization_get_dict(),
        active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Base.csv",
        ["Goalie", "Utilization Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Utilization/utilization_base.png")))

    # apply correction
    goalie_utilization = apply_sigmoid_correction(
        goalie_utilization_get_dict())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected", "Team"], goalie_utilization,
        active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Utilization/utilization_corrected.png")))


def goalie_win_rating() -> None:
    goalie_win_rating_calculate(active_players['Goalie'])
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating_Base.csv",
        ["Goalie", "Win Rating Base", "Team"], goalie_win_rating_get_dict(),
        active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating_Base.csv",
        ["Goalie", "Win Rating Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Win_Rating/win_rating_base.png")))

    # apply correction
    goalie_win_rating = apply_sigmoid_correction(
        goalie_win_rating_get_dict())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating_Corrected.csv",
        ["Goalie", "Win Rating Corrected", "Team"], goalie_win_rating,
        active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Win_Rating_Corrected.csv",
        ["Goalie", "Win Rating Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Win_Rating/win_rating_corrected.png")))


def goalie_save_percentage() -> None:
    sp_metrics = goalie_save_percentage_get_data(active_players["Goalie"])

    # these metrics being unevenly weighted it makes more sense to do sigmoid
    # correction after combining all the metrics
    goalie_save_percentage_combine_metrics(sp_metrics, active_players["Goalie"],
        team_stats)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Base.csv",
        ["Goalie", "Save Percentage Base", "Team"],
        goalie_save_percentage_get_dict(), active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Base.csv",
        ["Goalie", "Save Percentage Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Percentage/save_percentage_base.png")))

    # scale the save percentages by the number of saves to account for volume
    sp_metrics = goalie_save_percentage_scale_for_volume(sp_metrics,
        active_players["Goalie"])
    
    # these metrics being unevenly weighted it makes more sense to do sigmoid
    # correction after combining all the metrics
    goalie_save_percentage_combine_metrics(sp_metrics, active_players["Goalie"],
        team_stats)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled", "Team"],
        goalie_save_percentage_get_dict(), active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Percentage/save_percentage_scaled.png")))

    # apply correction
    goalie_save_percentage = apply_sigmoid_correction(
        goalie_save_percentage_get_dict())
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected", "Team"], goalie_save_percentage,
        active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Percentage/save_percentage_corrected.png")))


def goalie_goals_against_avg() -> None:
    goalie_goals_against_get_data(active_players["Goalie"])
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base", "Team"],
        goalie_goals_against_get_dict(), active_players['Goalie'], False)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Goals_Against/goals_against_base.png", True)))

    # apply correction
    goalie_goals_against = apply_sigmoid_correction(
        goalie_goals_against_get_dict(), True)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected", "Team"],
        goalie_goals_against, active_players['Goalie'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goals_Against/goals_against_corrected.png")))


def calculate_goalie_metrics() -> None:

    print("\tGoalie Utilization")
    goalie_utilization()
    print("\tGoalie Win Rating")
    goalie_win_rating()
    print("\tGoalie Save Percetage Rating")
    goalie_save_percentage()
    print("\tGoalie Goals Against Avg")
    goalie_goals_against_avg()
    goalie_total_rating = {}

    # not all active goalies have stats, but all metrics are generated for the
    # same subset of goalies so just loop through the keys of any metric
    print("\tCombining Goalie Metrics")
    for goalie in goalie_utilization_get_dict().keys():
        goalie_total_rating[goalie] = \
            (goalie_utilization_get_dict()[goalie] * \
                goalie_rating_weights.UTILIZATION_WEIGHT.value) + \
            (goalie_win_rating_get_dict()[goalie] * \
                goalie_rating_weights.WIN_RATING_WEIGHT.value) + \
            (goalie_save_percentage_get_dict()[goalie] * \
                goalie_rating_weights.SAVE_PERCENTAGE_WEIGHT.value) + \
            (goalie_goals_against_get_dict()[goalie] * \
                goalie_rating_weights.GOALS_AGAINST_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goalie_Total_Rating.csv",
        ["Goalie", "Total Rating", "Team"], goalie_total_rating,
        active_players['Goalie'])
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Goalie_Total_Rating.csv",
        ["Goalie", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goalie_Total_Rating/goalie_total_rating.png")


def defensemen_hits() -> None:
    defensemen_hits_get_data(active_players["Defenseman"])
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Base.csv",
        ["Defensemen", "Hits Base", "Team"],
        defensemen_hits_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Base.csv",
        ["Defensemen", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Hits/hits_base.png", False)))

    # apply correction
    defensemen_hits = apply_sigmoid_correction(
        defensemen_hits_get_dict(), False)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected", "Team"],
        defensemen_hits, active_players['Defenseman'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Hits/hits_corrected.png")))


def defensemen_blocks() -> None:
    defensemen_blocks_get_data(active_players["Defenseman"])
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Base.csv",
        ["Defensemen", "Blocks Base", "Team"],
        defensemen_blocks_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Base.csv",
        ["Defensemen", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Blocks/blocks_base.png", False)))

    # apply correction
    defensemen_blocks = apply_sigmoid_correction(
        defensemen_blocks_get_dict(), False)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected", "Team"],
        defensemen_blocks, active_players['Defenseman'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Blocks/blocks_corrected.png")))


def defensemen_utilization() -> None:
    utilization_metrics = defensemen_utilization_get_data(
        active_players["Defenseman"], team_stats)

    # plot each metric before sigmoid
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base", "Team"],
        utilization_metrics[0], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/even_utilzation_base.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Base.csv",
        ["Defensemen", "Power Play Utilization Base", "Team"],
        utilization_metrics[1], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Base.csv",
        ["Defensemen", "Power Play Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/pp_utilization_base.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Base.csv",
        ["Defensemen", "Penalty Kill Utilization Base", "Team"],
        utilization_metrics[2], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Base.csv",
        ["Defensemen", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/pk_utilization_base.png", False)))

    # apply sigmoids to uncombined values
    for metric_dict in utilization_metrics:
        apply_sigmoid_correction(metric_dict)

    # plot after individual sigmoids
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Corrected.csv",
        ["Defensemen", "Even Strength Utilization Corrected", "Team"],
        utilization_metrics[0], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Corrected.csv",
        ["Defensemen", "Even Strength Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/even_utilzation_corrected.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Corrected.csv",
        ["Defensemen", "Power Play Utilization Corrected", "Team"],
        utilization_metrics[1], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Corrected.csv",
        ["Defensemen", "Power Play Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/pp_utilization_corrected.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Corrected.csv",
        ["Defensemen", "Penalty Kill Utilization Corrected", "Team"],
        utilization_metrics[2], active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Corrected.csv",
        ["Defensemen", "Penalty Kill Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/pk_utilization_corrected.png", False)))

    # combine all metrics and then plot final score
    defensemen_utilization_combine_metrics(utilization_metrics)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/UtilizationRating.csv",
        ["Defensemen", "Utilization Rating", "Team"],
        defensemen_utilization_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/UtilizationRating.csv",
        ["Defensemen", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/utilization_rating.png", False)))


def defensemen_discipline() -> None:
    defensemen_discipline_get_data(active_players["Defenseman"])
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Base.csv",
        ["Defensemen", "Discipline Base", "Team"],
        defensemen_discipline_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Base.csv",
        ["Defensemen", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Discipline/discipline_base.png", False)))

    # apply correction
    defensemen_discipline = apply_sigmoid_correction(
        defensemen_discipline_get_dict(), False)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected", "Team"],
        defensemen_discipline, active_players['Defenseman'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Discipline/discipline_corrected.png")))


def defensemen_plus_minus() -> None:
    defensemen_plus_minus_get_data(active_players["Defenseman"])
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base", "Team"],
        defensemen_plus_minus_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Plus_Minus/plus_minus_base.png", False)))

    # apply correction
    defensemen_plus_minus = apply_sigmoid_correction(
        defensemen_plus_minus_get_dict(), False)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected", "Team"],
        defensemen_plus_minus, active_players['Defenseman'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Plus_Minus/plus_minus_corrected.png")))


def defensemen_points() -> None:
    defensemen_points_get_data(active_players["Defenseman"])
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Points_Base.csv",
        ["Defensemen", "Points Base", "Team"],
        defensemen_points_get_dict(), active_players['Defenseman'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Points_Base.csv",
        ["Defensemen", "Points Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Points/points_base.png", False)))

    # apply correction
    defensemen_points = apply_sigmoid_correction(
        defensemen_points_get_dict(), False)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Points_Corrected.csv",
        ["Defensemen", "Points Corrected", "Team"],
        defensemen_points, active_players['Defenseman'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Points_Corrected.csv",
        ["Defensemen", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Points/points_corrected.png")))


def calculate_defensemen_metrics() -> None:
    print("\tDefensemen Hits")
    defensemen_hits()

    print("\tDefensemen Blocks")
    defensemen_blocks()

    print("\tDefensemen Utilization")
    defensemen_utilization()

    print("\tDefensemen Discipline")
    defensemen_discipline()

    print("\tDefensemen Plus Minus")
    defensemen_plus_minus()

    print("\tDefensemen Points")
    defensemen_points()

    defensemen_total_rating = {}

    # not all active defensemen have stats, but all metrics are generated for
    # the same subset of defensemen so just loop through the keys of any metric
    print("\tCombining Defensemen Metics")
    for defensemen in defensemen_hits_get_dict().keys():
        defensemen_total_rating[defensemen] = \
            (defensemen_hits_get_dict()[defensemen] * \
                defensemen_rating_weights.HITS_WEIGHT.value) + \
            (defensemen_blocks_get_dict()[defensemen] * \
                defensemen_rating_weights.SHOT_BLOCKING_WEIGHT.value) + \
            (defensemen_utilization_get_dict()[defensemen] * \
                defensemen_rating_weights.UTILIZATION_WEIGHT.value) + \
            (defensemen_discipline_get_dict()[defensemen] * \
                defensemen_rating_weights.DISIPLINE_WEIGHT.value) + \
            (defensemen_plus_minus_get_dict()[defensemen] * \
                defensemen_rating_weights.PLUS_MINUS_WEIGHT.value) + \
            (defensemen_points_get_dict()[defensemen] * \
                defensemen_rating_weights.POINTS_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/" + \
            "Defensemen_Total_Rating.csv",
        ["Defensemen", "Total Rating", "Team"], defensemen_total_rating,
        active_players['Defenseman'])
    plot_player_ranking(
        "Output_Files/Defensemen_Files/Instance_Files/" + \
            "Defensemen_Total_Rating.csv",
        ["Defensemen", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Defensemen_Total_Rating/defensemen_total_rating.png")


def forward_points() -> None:
    forward_points_get_data(active_players["Forwards"])
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Points_Base.csv",
        ["Forward", "Points Base", "Team"],
        forward_points_get_dict(), active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Points_Base.csv",
        ["Forward", "Points Base"], 0.0, 0.0, [],
        "Graphs/Forward/Points/points_base.png", False)))

    # apply correction
    forward_points = apply_sigmoid_correction(
        forward_points_get_dict(), False)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Points_Corrected.csv",
        ["Forward", "Points Corrected", "Team"],
        forward_points, active_players['Forwards'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Points_Corrected.csv",
        ["Forward", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Points/points_corrected.png")))


def forward_utilization() -> None:
    utilization_metrics = forward_utilization_get_data(
        active_players["Forwards"] , team_stats)

    # plot each metric before sigmoid
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base", "Team"],
        utilization_metrics[0], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/even_utilzation_base.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Base.csv",
        ["Forward", "Power Play Utilization Base", "Team"],
        utilization_metrics[1], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Base.csv",
        ["Forward", "Power Play Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/pp_utilization_base.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Base.csv",
        ["Forward", "Penalty Kill Utilization Base", "Team"],
        utilization_metrics[2], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Base.csv",
        ["Forward", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/pk_utilization_base.png", False)))

    # apply sigmoids to uncombined values
    for metric_dict in utilization_metrics:
        apply_sigmoid_correction(metric_dict)

    # plot after individual sigmoids
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Corrected.csv",
        ["Forward", "Even Strength Utilization Corrected", "Team"],
        utilization_metrics[0], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Corrected.csv",
        ["Forward", "Even Strength Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/even_utilzation_corrected.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Corrected.csv",
        ["Forward", "Power Play Utilization Corrected", "Team"],
        utilization_metrics[1], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Corrected.csv",
        ["Forward", "Power Play Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/pp_utilization_corrected.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Corrected.csv",
        ["Forward", "Penalty Kill Utilization Corrected", "Team"],
        utilization_metrics[2], active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Corrected.csv",
        ["Forward", "Penalty Kill Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/pk_utilization_corrected.png", False)))

    # combine all metrics and then plot final score
    forward_utilization_combine_metrics(utilization_metrics)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/UtilizationRating.csv",
        ["Forward", "Utilization Rating", "Team"],
        forward_utilization_get_dict(), active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/UtilizationRating.csv",
        ["Forward", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/utilization_rating.png", False)))


def forward_plus_minus() -> None:
    forward_plus_minus_get_data(active_players["Forwards"])
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base", "Team"],
        forward_plus_minus_get_dict(), active_players['Forwards'], True)
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Forward/Plus_Minus/plus_minus_base.png", False)))

    # apply correction
    forward_plus_minus = apply_sigmoid_correction(
        forward_plus_minus_get_dict(), False)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected", "Team"],
        forward_plus_minus, active_players['Forwards'])
    player_eng_plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Plus_Minus/plus_minus_corrected.png")))


def calculate_forward_metrics() -> None:
    print("\tForward Utilization")
    forward_utilization()
    print("\tForward Points")
    forward_points()
    print("\tForward Plus Minus")
    forward_plus_minus()

    forward_total_rating = {}

    # not all active forward have stats, but all metrics are generated for the
    # same subset of forward so just loop through the keys of any metric
    print("\tCombining Forward Metrics")
    for forward in forward_points_get_dict().keys():
        forward_total_rating[forward] = \
            (forward_utilization_get_dict()[forward] * \
                forward_rating_weights.UTILIZATION_WEIGHT.value) + \
            (forward_points_get_dict()[forward] * \
                forward_rating_weights.POINTS_WEIGHT.value) + \
            (forward_plus_minus_get_dict()[forward] * \
                forward_rating_weights.PLUS_MINUS_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/" + \
            "Forward_Total_Rating.csv",
        ["Forward", "Total Rating", "Team"], forward_total_rating,
        active_players['Forwards'])
    plot_player_ranking(
        "Output_Files/Forward_Files/Instance_Files/" + \
            "Forward_Total_Rating.csv",
        ["Forward", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Forward_Total_Rating/forward_total_rating.png")


if __name__ == "__main__":

    # set up multiprocess to be ready in case a subprocess freezes
    freeze_support()
    start = time.time()

    # create a few plotting processes to speed things up a bit
    subprocess_count = 15
    process_list = []
    for i in range(subprocess_count):
        process_list.append(Process(target=plotter_worker,
            args=(player_eng_plotting_queue, i)))
    for process in process_list:
        process.start()

    # get all players and sort them into the list for their position
    print("Sorting All Active Players by Position")
    player_sorting()
    get_team_stats()

    # GOALIES
    print("Calculating all Goalie Metrics:")
    calculate_goalie_metrics()
    print("Calculating all Defensemen Metrics:")
    calculate_defensemen_metrics()
    print("Calculation all Forward Metrics")
    calculate_forward_metrics()
    print("Waiting for Plotters to finish their very hard work <3")

    # stop all the running workers
    for i in range(subprocess_count):
        player_eng_plotting_queue.put('STOP')
    for process in process_list:
        while process.is_alive():
            pass

    # remove all the instance files
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Goalie_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Goalie_Files\Instance_Files\\" + file)
    print(time.time() - start)
