from multiprocessing import Process, Queue, freeze_support
import time
import csv
import datetime
from enum import Enum
import tkinter as tk
from tkinter.ttk import *
from copy import copy

from Database_Parser import get_game_records

from User_Interface_Main import get_main_window, get_widget, \
    construct_main_menu, add_progress_frame, close_progress_frame, \
    display_error_window, update_progress_text, update_progress_bar

from League_Stats.Shooting_Percentage import \
    shooting_percentage_get_shpct_by_zone_get_dict, \
    shooting_percentage_get_shots_dict, shooting_percentage_get_goals_dict, \
    shooting_percentage_add_match_data, \
    shooting_percentage_calculate_league_values

# import all custom team modules for statistical analysis
from Team_Metrics.Clutch import Clutch
from Team_Metrics.Goal_Differential import Goal_Differential
from Team_Metrics.Penalty_Kill import Penalty_Kill
from Team_Metrics.Power_Play import Power_Play
from Team_Metrics.Recent_Form import Recent_Form
from Team_Metrics.Shot_Differential import Shot_Differential
from Team_Metrics.Strength_of_Schedule import Strength_of_Schedule

# import all custom player modules for statistical analysis
from Player_Metrics.Utilization import Utilization
from Player_Metrics.Blocked_Shots import Blocked_Shots
from Player_Metrics.Contributing_Games import Contributing_Games
from Player_Metrics.Discipline import Discipline
from Player_Metrics.Hitting import Hitting
from Player_Metrics.Muiltipoint_Games import Multipoint_Games
from Player_Metrics.PlusMinus import PlusMinus
from Player_Metrics.Total_Points import Total_Points
from Player_Metrics.Turnovers import Turnovers
from Player_Metrics.Goals_Against import Goals_Against
from Player_Metrics.Save_Consistency import Save_Consistency
from Player_Metrics.Save_Percentage import Save_Percentage

# shared engine tools
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import team_weights, goalie_weights, \
    forward_weights, defenseman_weights, divisions, \
    EYE_TEST_WEIGHT
from Plotter import plot_data_set, plot_team_trend_set, plot_player_trend_set, \
    plot_player_ranking, plot_matches_ranking
from CSV_Writer import write_out_file, update_trend_file, write_out_player_file, \
    write_out_matches_file

sigmoid_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

team_total_rating = {}

goalie_total_rating = {}

forward_total_rating = {}

defensemen_total_rating = {}

total_rating_trend = {}

ranking_absolutes = {}

ranking_averages = {}

average_goalie_rating = {}

average_forward_rating = {}

average_defenseman_rating = {}

average_player_rating = {}

goalie_teams = {}

forward_teams = {}

defensemen_teams = {}

player_eye_test_rating = {}

regular_season_matches = {}

playoff_matches = {}

upcoming_matches = {}

upcoming_playoff_matches = {}

expected_goals_by_zone = {
    "neutral_zone" : 0.0,
    "distance" : 0.0,
    "high_danger" : 0.0,
    "netfront" : 0.0,
    "behind_net": 0.0,
    "corners" : 0.0,
    "outside" : 0.0,
}

match_input_queue = Queue()
match_output_queue = Queue()
plotting_queue = Queue()
dummy_queue = Queue()
plots_count = 0

class Metric_Order(Enum):
    CLUTCH = 0
    DEFENSIVE = 1
    OFFENSIVE = 2
    RECENT = 3
    SOS = 4
    TOTAL = 5

class Team_Selection(Enum):
    HOME = 0
    AWAY = 1

# metric class instances
clutch_metric = Clutch()
goal_differential_metric = Goal_Differential()
penalty_kill_metric = Penalty_Kill()
power_play_metric = Power_Play()
recent_form_metric = Recent_Form()
shot_differential_metric = Shot_Differential()
strength_of_schedule_metric = Strength_of_Schedule()

team_metrics = [clutch_metric, goal_differential_metric, penalty_kill_metric,
    power_play_metric, recent_form_metric, shot_differential_metric,
    strength_of_schedule_metric]

utilization_metric = Utilization()
blocked_shots_metric = Blocked_Shots()
contributing_games_metric = Contributing_Games()
discipline_metric = Discipline()
hitting_metric = Hitting()
multipoint_game_metric = Multipoint_Games()
plus_minus_metric = PlusMinus()
total_points_metric = Total_Points()
turnovers_metric = Turnovers()
goals_against_metric = Goals_Against()
save_consistency_metric = Save_Consistency()
save_percentage_metric = Save_Percentage()

goalie_metrics_list = [utilization_metric, goals_against_metric,
    save_consistency_metric, save_percentage_metric, discipline_metric]

player_metrics_list = [utilization_metric, blocked_shots_metric,
    contributing_games_metric, discipline_metric, hitting_metric,
    multipoint_game_metric, plus_minus_metric, total_points_metric,
    turnovers_metric]

def print_time_diff(start_time : float=0.0, end_time : float=0.0) -> None:
    print("Completed in {} seconds".format(end_time - start_time))


def parse_eye_test_file(file_name : str="") -> int:
    try:
        with open(file_name, "r", newline='', encoding='utf-16') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                player_eye_test_rating[row[0]] = row[1]
        csv_file.close()
        return 0
    except FileNotFoundError:
        ("The file you have entered does not exist")
        return -1


def worker_node(input_queue : Queue=None, output_queue : Queue=None) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    output_queue.put('STOP')


def get_team_trend_by_date(home_team : str="", away_team : str="",
    ranking_date : str="") -> dict:

    relative_rankings = {
        'clutch' : {
            'home' : clutch_metric.get_relative_ranking_by_date(ranking_date, 
                home_team),
            'away' : clutch_metric.get_relative_ranking_by_date(ranking_date, 
                away_team)
        },
        'goal_differential' : {
            'home' : goal_differential_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : goal_differential_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'penalty_kill' : {
            'home' : penalty_kill_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : penalty_kill_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'power_play' : {
            'home' : power_play_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : power_play_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'recent_form' : {
            'home' : recent_form_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : recent_form_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'shot_differential' : {
            'home' : shot_differential_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : shot_differential_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'strength_of_schedule' : {
            'home' : strength_of_schedule_metric.get_relative_ranking_by_date(
                ranking_date, home_team),
            'away' : strength_of_schedule_metric.get_relative_ranking_by_date(
                ranking_date, away_team)
        },
        'total' : {'home' : 0.5, 'away' : 0.5}
    }

    if ranking_date == "":
        return relative_rankings

    # if the home team does not have a ranking because they have not
    # played yet then default them to 0.5, same for away
    if not (home_team in total_rating_trend[ranking_date]):
        ranking_absolutes[ranking_date][home_team] = 0.5
        ranking_averages[ranking_date][home_team] = 0.5
        total_rating_trend[ranking_date][home_team] = 0.5
    if not (away_team in total_rating_trend[ranking_date]):
        ranking_absolutes[ranking_date][away_team] = 0.5
        ranking_averages[ranking_date][away_team] = 0.5
        total_rating_trend[ranking_date][away_team] = 0.5

    # if either team has played less than 5 games, we cant get a real score from
    # them so just set to .5
    if (home_team in strength_of_schedule_metric.
        get_games_played_dict().keys()):

        if (strength_of_schedule_metric.get_games_played_dict()[home_team] < 5):
            relative_rankings["clutch"]['home'] = 0.5
            relative_rankings["goal_differential"]['home'] = 0.5
            relative_rankings["penalty_kill"]['home'] = 0.5
            relative_rankings["power_play"]['home'] = 0.5
            relative_rankings["recent_form"]['home'] = 0.5
            relative_rankings["shot_differential"]['home'] = 0.5
            relative_rankings["strength_of_schedule"]['home'] = 0.5
            relative_rankings["total"]['home'] = 0.5

    if (away_team in strength_of_schedule_metric.
        get_games_played_dict().keys()):

        if (strength_of_schedule_metric.get_games_played_dict()[away_team] < 5):
            relative_rankings["clutch"]['away'] = 0.5
            relative_rankings["goal_differential"]['away'] = 0.5
            relative_rankings["penalty_kill"]['away'] = 0.5
            relative_rankings["power_play"]['away'] = 0.5
            relative_rankings["recent_form"]['away'] = 0.5
            relative_rankings["shot_differential"]['away'] = 0.5
            relative_rankings["strength_of_schedule"]['away'] = 0.5
            relative_rankings["total"]['away'] = 0.5

    return relative_rankings


def parse_team_match_data(match_data : dict={}, relative_metrics : dict={}) \
                                                                        -> list:
    metric_data = {"team_data" : {}}

    # get home and away team
    away_team = match_data["game_stats"]["away_team"]
    home_team = match_data["game_stats"]["home_team"]

    # loop through all team metrics
    for metric in team_metrics:

        # get the initial data set which can take almost any form, but is
        # always returned as a dicts with the root keys as home_team and
        # away_team
        temp_metric_data = metric.get_data_set(match_data)

        # print(metric)
        # print(temp_metric_data)

        # apply the relative scaling. This will be unique to basically every
        # metric
        temp_metric_data[home_team] = metric.apply_relative_scaling(
            relative_metrics[metric.get_comparator()]['home'],
            temp_metric_data[home_team]
        )
        temp_metric_data[away_team] = metric.apply_relative_scaling(
            relative_metrics[metric.get_comparator()]['away'],
            temp_metric_data[away_team]
        )

        # copy the metric over so we don't overwrite in the next loop step
        metric_data['team_data'][metric.name] = copy(temp_metric_data)
    return metric_data


def parse_player_match_data(match_data : dict={}, relative_metrics : dict={},
    player_list : list=[]) -> list:

    metric_data = {"player_data" : {}}
    goalie_metrics = {}
    forward_metrics = {}
    defensemen_metrics = {}
    goalies = player_list[0]
    forwards = player_list[1]
    defensemen = player_list[2]

    # get home and away team
    home_team = match_data["game_stats"]["home_team"]

    # collect all data and apply relative scaling for goalies
    for goalie in goalies:

        # run throught all metrics
        for metric in goalie_metrics_list:

            # get the next set of data for the next metric in the list
            temp_metric_data = metric.get_data_set(goalies)

            # if the player is on the home team
            if goalies[goalie]['team'] == home_team:
                temp_metric_data[goalie] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['away'],
                        temp_metric_data[goalie]
                    )
                )

            # if the player is on the away team
            else:
                temp_metric_data[goalie] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['home'],
                        temp_metric_data[goalie]
                    )
                )
            
            # add the metric to the data set for all goalie metrics passed on
            goalie_metrics[metric.name] = copy(temp_metric_data)

    ### Forward metrics
    for forward in forwards:

        # run throught all metrics
        for metric in player_metrics_list:

            # get the next set of data for the next metric in the list
            temp_metric_data = metric.get_data_set(forwards)

            # if the player is on the home team
            if forwards[forward]['team'] == home_team:
                temp_metric_data[forward] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['away'],
                        temp_metric_data[forward]
                    )
                )

            # if the player is on the away team
            else:
                temp_metric_data[forward] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['home'],
                        temp_metric_data[forward]
                    )
                )
            
            # add the metric to the data set for all forward metrics passed on
            forward_metrics[metric.name] = copy(temp_metric_data)

    ### Defensemen Metrics
    for defenseman in defensemen:

        # run throught all metrics
        for metric in player_metrics_list:

            # get the next set of data for the next metric in the list
            temp_metric_data = metric.get_data_set(defensemen)

            # if the player is on the home team
            if defensemen[defenseman]['team'] == home_team:
                temp_metric_data[defenseman] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['away'],
                        temp_metric_data[defenseman]
                    )
                )

            # if the player is on the away team
            else:
                temp_metric_data[defenseman] = (
                    metric.apply_relative_scaling(
                        relative_metrics[metric.get_comparator()]['home'],
                        temp_metric_data[defenseman]
                    )
                )
            
            # add the metric to the data set for all forward metrics passed on
            defensemen_metrics[metric.name] = copy(temp_metric_data)

    # Append all player metrics
    metric_data['player_data']['goalie_metrics'] = goalie_metrics
    metric_data['player_data']['forward_metrics'] = forward_metrics
    metric_data['player_data']['defensemen_metrics'] = defensemen_metrics
    return(metric_data)


def parse_play_by_play_data(match_data : dict={}, relative_metrics : list=[]):
    metric_data = {"play_by_play_data" : {
        "penalties" : [],
        "hits" : [],
        "takeaways" : [],
        "giveaways" : [],
        "shots" : [],
        "faceoffs" : [],
        "goals" : [],
    }}

    zone_stats = match_data["game_stats"]["zone_stats"]

    # for now we don't do anything so just move the data links over and return
    metric_data["play_by_play_data"]["penalties"] = zone_stats["penalties"]
    metric_data["play_by_play_data"]["hits"] = zone_stats["hits"]
    metric_data["play_by_play_data"]["takeaways"] = zone_stats["takeaways"]
    metric_data["play_by_play_data"]["giveaways"] = zone_stats["giveaways"]
    metric_data["play_by_play_data"]["shots"] = zone_stats["shots"]
    metric_data["play_by_play_data"]["faceoffs"] = zone_stats["faceoffs"]
    metric_data["play_by_play_data"]["goals"] = zone_stats["goals"]
    return(metric_data)
    

def run_match_parser(match_dates : list=[], ranking_date : str="",
    matches_list : list=[]) -> None:

    # get all the different parsed trend data dictionaries
    for date in match_dates:
        for match in matches_list[date]:

            ################ TEAMS #####################
            # get the home and away team
            away_team = match["game_stats"]["away_team"]
            home_team = match["game_stats"]["home_team"]
            trends_by_date = get_team_trend_by_date(home_team, away_team,
                ranking_date)

            ##################### PLAYERS ######################
            goalies = {}
            forwards = {}
            defensemen = {}
            players = match["game_stats"][home_team]["player_stats"]
            for player_by_ID in players.keys():

                # find the players position
                # if we can't determine the position, skip getting stats
                position = players[player_by_ID]["player_position"]

                # read out the players name
                name = players[player_by_ID]["player_name"]

                # determine if the player had any stats for this game based
                # on if they played at least 1 second of game time.
                time_on_ice = (
                    float(players[player_by_ID]["time_on_ice"].split(":")[0]) +
                    (float(players[player_by_ID]["time_on_ice"].split(":")[1]) 
                        / 60)
                )
                if time_on_ice > 0:
                    stats = players[player_by_ID]
                else:
                    stats = None

                # sort all the players in this match to parse their data
                if (position == 'G') and (stats != None):
                    goalies[name] = {'team' : home_team, 'stats' : stats}
                elif (position == 'D') and (stats != None):
                    defensemen[name] = {'team' : home_team, 'stats' : stats}
                elif (stats != None):
                    forwards[name] = {'team' : home_team, 'stats' : stats}

            # then do away team players
            players = match["game_stats"][away_team]["player_stats"]
            for player_by_ID in players.keys():

                # find the players position
                # if we can't determine the position, skip getting stats
                position = players[player_by_ID]["player_position"]

                # read out the players name
                name = players[player_by_ID]["player_name"]

                # determine if the player had any stats for this game based
                # on if they played at least 1 second of game time.
                time_on_ice = (
                    float(players[player_by_ID]["time_on_ice"].split(":")[0]) +
                    (float(players[player_by_ID]["time_on_ice"].split(":")[1]) 
                        / 60)
                )
                if time_on_ice > 0:
                    stats = players[player_by_ID]
                else:
                    stats = None

                # sort all the players in this match to parse their data
                if (position == 'G') and (stats != None):
                    goalies[name] = {'team' : away_team, 'stats' : stats}
                elif (position == 'D') and (stats != None):
                    defensemen[name] = {'team' : away_team, 'stats' : stats}
                elif (stats != None):
                    forwards[name] = {'team' : away_team, 'stats' : stats}

            # feed the match information with the scale factors for each team
            # into the match parser which will call all metrics to get all
            # relevant information required
            match_input_queue.put((parse_team_match_data,
                (match, trends_by_date)))
            match_input_queue.put((parse_player_match_data,
                (match, trends_by_date, [goalies, forwards, defensemen])))
            # match_input_queue.put((parse_play_by_play_data,
            #     (match, trends_by_date)))
            

def plot_uncorrected_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    # get data for each relevent metric
    for metric in team_metrics:
        arg_list = metric.get_uncorrected_print_args(prefix)

        # some metrics need to print more than one set of data so it is returned
        # as a list thjat can be looped through with the same format for each
        # element
        for data_set in arg_list:
            write_out_file(data_set["data_file_name"], data_set["title_args"],
                data_set["data_dict"])
            plotting_queue.put((plot_data_set, (
                data_set["data_file_name"],
                data_set["title_args"], 0.0, 0.0, [], data_set["graph_name"],
                data_set["ascending_order"]
            )))


def plot_corrected_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    # get data for each relevent metric
    for metric in team_metrics:
        arg_list = metric.get_corrected_print_args(prefix)

        # some metrics need to print more than one set of data so it is returned
        # as a list thjat can be looped through with the same format for each
        # element
        for data_set in arg_list:
            write_out_file(data_set["data_file_name"], data_set["title_args"],
                data_set["data_dict"])
            plotting_queue.put((plot_data_set, (
                data_set["data_file_name"],
                data_set["title_args"], 0.0, 0.0, [], data_set["graph_name"],
                data_set["ascending_order"]
            )))
    

def plot_combined_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}TotalRating.csv".format(
            prefix
        ),
        ["Team", "Total Rating"], team_total_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}TotalRating.csv".format(
            prefix
        ),
        ["Team", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/{}final_rating_score.png".format(
            prefix
        ))))
    

def plot_trend_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    # get data for each relevent metric
    for metric in team_metrics:
        arg_list = metric.get_trend_print_args(prefix)

        # some metrics need to print more than one set of data so it is returned
        # as a list thjat can be looped through with the same format for each
        # element
        for data_set in arg_list:
            write_out_file(data_set["data_file_name"], data_set["title_args"],
                data_set["data_dict"])
            plotting_queue.put((plot_data_set, (
                data_set["data_file_name"],
                data_set["title_args"], 0.0, 0.0, [], data_set["graph_name"],
                data_set["ascending_order"]
            )))

    # absolute ranking
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}AbsoluteRankings.csv".format(
            prefix
        ),
        ranking_absolutes, "Absolute Ranking")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}AbsoluteRankings.csv".format(
            prefix
        ),
        ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Teams/Final_Rating_Score/{}absolute_ranking_trend.png".format(
            prefix
        ))))

    # average ranking
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}AverageRankings.csv".format(
            prefix
        ),
        ranking_averages, "Average Ranking")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}AverageRankings.csv".format(
            prefix
        ),
        ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Teams/Final_Rating_Score/{}average_ranking_trend.png".format(
            prefix
        ))))

    # final rating
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}RatingScore.csv".format(
            prefix
        ),
        total_rating_trend, "Rating Score")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}RatingScore.csv".format(
            prefix
        ),
        ["Rating Date", "Rating Score"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/{}rating_score_trend.png".format(
            prefix
        ))))
    

def plot_average_player_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    # Average Goalie Ranking
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}AvgGoalie.csv".format(
            prefix
        ),
        ["Team", "Average Goalie"], average_goalie_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}AvgGoalie.csv".format(
            prefix
        ),
        ["Team", "Average Goalie"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/{}".format(prefix) +
            "average_goalie_rating.png",
        True)
    ))
    
    # Average Forward Ranking
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}AvgForward.csv".format(
            prefix
        ),
        ["Team", "Average Forward"], average_forward_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}AvgForward.csv".format(
            prefix
        ),
        ["Team", "Average Forward"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/{}".format(prefix) +
            "average_forward_rating.png",
        True)
    ))
    
    # Average Defensemen Ranking
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}AvgDefenseman.csv".format(
            prefix
        ),
        ["Team", "Average Defenseman"], average_defenseman_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}AvgDefenseman.csv".format(
            prefix
        ),
        ["Team", "Average Defenseman"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/" +
            "{}average_defenseman_rating.png".format(prefix),
        True)
    ))
    
    # Average Roster Ranking
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}AvgPlayer.csv".format(prefix),
        ["Team", "Average Player"], average_player_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}AvgPlayer.csv".format(prefix),
        ["Team", "Average Player"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/{}".format(prefix) +
            "average_player_rating.png",
        True)
    ))


def plot_uncorrected_player_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    ### Goalies
    # Utilization
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Base.csv",
        ["Goalie", "Utilization Base", "Team"],
        utilization_metric.get_base_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Base.csv",
        ["Goalie", "Utilization Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Utilization/{}utilization_base.png".format(prefix))
    ))
    
    # Goals Against
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base", "Team"],
        goals_against_metric.get_base_rating_dict("G"), goalie_teams,
        False)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Goals_Against/{}goals_against_base.png".format(prefix),
        True)
    ))
    
    # Save Percentage
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled", "Team"],
        save_percentage_metric.get_base_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Percentage/{}save_percentage_scaled.png".format(
            prefix
        ))
    ))
    
    # Save Consistency
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Base.csv",
        ["Goalie", "Save Consistency Base", "Team"],
        save_consistency_metric.get_base_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Base.csv",
        ["Goalie", "Save Consistency Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Consistency/{}save_consistency_base.png".format(
            prefix
        ))
    ))
    
    ### Forwards
    # Blocks
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}Blocks_Base.csv".format(
            prefix),
        ["Forward", "Blocks Base", "Team"],
        blocked_shots_metric.get_base_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Forward_Files/Instance_Files/{}Blocks_Base.csv".format(
            prefix),
        ["Forward", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Forward/Blocks/{}blocks_base.png".format(prefix)
        )
    ))
    
    # Contributing Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Base.csv",
        ["Forward", "Contribution Base", "Team"],
        contributing_games_metric.get_base_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Base.csv",
        ["Forward", "Contribution Base"], 0.0, 0.0, [],
        "Graphs/Forward/Contribution/{}contribution_base.png".format(prefix))
    ))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Forward", "Discipline Base", "Team"],
        discipline_metric.get_base_rating_dict("C"), forward_teams, False)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Forward", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Forward/Discipline/{}discipline_base.png".format(prefix),
        True)
    ))
    
    # Hits
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix
        ),
        ["Forward", "Hits Base", "Team"],
        hitting_metric.get_base_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix),
        ["Forward", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Forward/Hits/{}hits_base.png".format(prefix), False)))
    
    # Multipoint Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Base.csv",
        ["Forward", "Multipoint Base", "Team"],
        multipoint_game_metric.get_base_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Base.csv",
        ["Forward", "Multipoint Base"], 0.0, 0.0, [],
        "Graphs/Forward/Multipoint/{}Multipoint_base.png".format(prefix),
        False)
    ))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base", "Team"],
        plus_minus_metric.get_base_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Forward/Plus_Minus/{}plus_minus_base.png".format(prefix),
        False)
    ))
    
    # Turnovers
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}Turnovers_Base.csv".format(
            prefix
        ),
        ["Forward", "Turnovers Base", "Team"],
        turnovers_metric.get_base_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/{}Turnovers_Base.csv".format(
            prefix
        ),
        ["Forward", "Turnovers Base"], 0.0, 0.0, [],
        "Graphs/Forward/Turnovers/{}takeaways_base.png".format(prefix),
            False)
    ))
    
    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Base.csv",
        ["Forward", "Points Base", "Team"],
        total_points_metric.get_base_rating_dict("C"), forward_teams,
        True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Base.csv",
        ["Forward", "Points Base"], 0.0, 0.0, [],
        "Graphs/Forward/Total_Points/{}total_points_base.png".format(prefix),
        False)
    ))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base", "Team"],
        utilization_metric.get_base_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/{}even_utilzation_base.png".format(prefix),
        False)
    ))
    
    ### Defensemen
    # Blocks
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}Blocks_Base.csv".format(
            prefix),
        ["Defensemen", "Blocks Base", "Team"],
        blocked_shots_metric.get_base_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Base.csv",
        ["Defensemen", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Blocks/{}blocks_base.png".format(prefix))
    ))

    # Contributing Games
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Base.csv",
        ["Defensemen", "Contribution Base", "Team"],
        contributing_games_metric.get_base_rating_dict("D"),
        defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Base.csv",
        ["Defensemen", "Contribution Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Contribution/{}contribution_base.png".format(prefix))
    ))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Defensemen", "Discipline Base", "Team"],
        discipline_metric.get_base_rating_dict("D"), defensemen_teams,
        False)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Defensemen", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Discipline/{}discipline_base.png".format(prefix),
        True)
    ))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base", "Team"],
        utilization_metric.get_base_rating_dict("D"), defensemen_teams,
        True)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/{}".format(prefix) +
            "even_utilzation_base.png",
        False)
    ))
    
    # Hits
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix),
        ["Defensemen", "Hits Base", "Team"],
        hitting_metric.get_base_rating_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix),
        ["Defensemen", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Hits/{}hits_base.png".format(prefix), False)
    ))

    # Multipoint Games
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Base.csv",
        ["Defensemen", "Multipoint Base", "Team"],
        multipoint_game_metric.get_base_rating_dict("D"), defensemen_teams,
        True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Base.csv",
        ["Defensemen", "Multipoint Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Multipoint/{}Multipoint_base.png".format(prefix),
        False)
    ))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base", "Team"],
        plus_minus_metric.get_base_rating_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Plus_Minus/{}plus_minus_base.png".format(prefix),
        False)
    ))
    
    # Points
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}Points_Base.csv".format(
            prefix),
        ["Defensemen", "Points Base", "Team"],
        total_points_metric.get_base_rating_dict("D"), defensemen_teams,
        True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Base.csv",
        ["Defensemen", "Points Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Total_Points/points_base.png".format(prefix),
        False)
    ))
    
    # Turnovers
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Base.csv",
        ["Defensemen", "Turnovers Base", "Team"],
        turnovers_metric.get_base_rating_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Base.csv",
        ["Defensemen", "Turnovers Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Turnovers/{}takeaways_base.png".format(prefix),
        False)
    ))


def plot_corrected_player_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    ### Goalies
    # Goals Against
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected", "Team"],
        goals_against_metric.get_final_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goals_Against/{}goals_against_corrected.png".format(
            prefix))
    ))

    # Save Consistency
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected", "Team"],
        save_consistency_metric.get_final_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Consistency/{}".format(prefix) +
            "save_consistency_corrected.png")
    ))
    
    # Save Percentage
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected", "Team"],
        save_percentage_metric.get_final_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Percentage/{}save_percentage_corrected.png".format(
            prefix))
        ))

    # Utilization
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected", "Team"],
        utilization_metric.get_final_rating_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Utilization/{}utilization_corrected.png".format(prefix))
    ))

    ### Forwards
    # Blocks
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Forward", "Blocks Corrected", "Team"],
        blocked_shots_metric.get_final_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Forward", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Blocks/{}blocks_corrected.png".format(prefix))
    ))

    # Contributing Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Corrected.csv",
        ["Forward", "Contribution Corrected", "Team"],
        contributing_games_metric.get_final_rating_dict("C"),
        forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Corrected.csv",
        ["Forward", "Contribution Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Contribution/{}".format(prefix) +
            "contribution_corrected.png")
    ))

    # Discipline
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Corrected.csv",
        ["Forward", "Discipline Corrected", "Team"],
        discipline_metric.get_final_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Corrected.csv",
        ["Forward", "Discipline Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Discipline/{}discipline_corrected.png".format(prefix))
    ))

    # Hits
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}Hits_Corrected.csv".format(
            prefix),
        ["Forward", "Hits Corrected", "Team"],
        hitting_metric.get_final_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Hits_Corrected.csv",
        ["Forward", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Hits/{}hits_corrected.png".format(prefix))
    ))

    # Multipoint Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Corrected.csv",
        ["Forward", "Multipoint Corrected", "Team"],
        multipoint_game_metric.get_final_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Corrected.csv",
        ["Forward", "Multipoint Corrected"], 0.0, 0.0, [],
        "Graphs/Forward/Multipoint/{}multipoint_corrected.png".format(prefix),
        False)
    ))

    # Plus Minus
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected", "Team"],
        plus_minus_metric.get_final_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Plus_Minus/{}plus_minus_corrected.png".format(prefix))
    ))

    # Turnovers
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Corrected.csv",
        ["Forward", "Turnovers Corrected", "Team"],
        turnovers_metric.get_final_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Corrected.csv",
        ["Forward", "Turnovers Corrected"], 0.0, 0.0, [],
        "Graphs/Forward/Turnovers/{}takeaways_corrected.png".format(prefix),
        False)
    ))

    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Corrected.csv",
        ["Forward", "Points Corrected", "Team"],
        total_points_metric.get_final_rating_dict("C"), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Corrected.csv",
        ["Forward", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Total_Points/{}total_points_corrected.png".format(
            prefix))))

    # Utilization
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "UtilizationRating.csv",
        ["Forward", "Utilization Rating", "Team"],
        utilization_metric.get_final_rating_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "UtilizationRating.csv",
        ["Forward", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/{}utilization_rating.png".format(prefix),
        False)
    ))

    ### Defensemen
    # Blocks
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected", "Team"],
        blocked_shots_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Blocks/{}blocks_corrected.png".format(prefix))
    ))

    # Contributing Games
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Corrected.csv",
        ["Defensemen", "Contribution Corrected", "Team"],
        contributing_games_metric.get_final_rating_dict("D"),
        defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Corrected.csv",
        ["Defensemen", "Contribution Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Contribution/{}".format(prefix) +
            "contribution_corrected.png")
    ))

    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected", "Team"],
        discipline_metric.get_final_rating_dict("D"),
        defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Discipline/{}discipline_corrected.png".format(
            prefix))
    ))

    # Hits
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected", "Team"],
        hitting_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Hits/{}hits_corrected.png".format(prefix))))

    # Multipoint Games
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Corrected.csv",
        ["Defensemen", "Multipoint Corrected", "Team"],
        multipoint_game_metric.get_final_rating_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Multipoint_Corrected.csv",
        ["Defensemen", "Multipoint Corrected"], 0.0, 0.0, [],
        "Graphs/Defensemen/Multipoint/{}multipoint_corrected.png".format(
            prefix),
        False)
    ))

    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected", "Team"],
        plus_minus_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Plus_Minus/{}plus_minus_corrected.png".format(prefix))
    ))

    # Points
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Corrected.csv",
        ["Defensemen", "Points Corrected", "Team"],
        total_points_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Corrected.csv",
        ["Defensemen", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Total_Points/{}points_corrected.png".format(prefix))
    ))

    # Turnovers
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Corrected.csv",
        ["Defensemen", "Turnovers Corrected", "Team"],
        turnovers_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Corrected.csv",
        ["Defensemen", "Turnovers Corrected"], 0.0, 0.0, [],
        "Graphs/Defensemen/Turnovers/{}takeaways_corrected.png".format(prefix))
    ))

    # Utilization
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "UtilizationRating.csv",
        ["Defensemen", "Utilization Rating", "Team"],
        utilization_metric.get_final_rating_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "UtilizationRating.csv",
        ["Defensemen", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/{}utilization_rating.png".format(prefix))
    ))


def plot_combined_player_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goalie_Total_Rating.csv",
        ["Goalie", "Total Rating", "Team"], goalie_total_rating, goalie_teams)
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goalie_Total_Rating.csv".format(prefix),
        ["Goalie", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goalie_Total_Rating/{}goalie_total_rating.png".format(
            prefix))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/" +
            "{}Forward_Total_Rating.csv".format(prefix),
        ["Forward", "Total Rating", "Team"], forward_total_rating,
        forward_teams)
    plot_player_ranking(
        "Output_Files/Forward_Files/Instance_Files/" +
            "{}Forward_Total_Rating.csv".format(prefix),
        ["Forward", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Forward_Total_Rating/{}forward_total_rating.png".format(
            prefix
    ))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/" +
            "{}Defensemen_Total_Rating.csv".format(prefix),
        ["Defensemen", "Total Rating", "Team"], defensemen_total_rating,
        defensemen_teams)
    plot_player_ranking(
        "Output_Files/Defensemen_Files/Instance_Files/" +
            "{}Defensemen_Total_Rating.csv".format(prefix),
        ["Defensemen", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Defensemen_Total_Rating/" +
            "{}defensemen_total_rating.png".format(prefix
    ))


def combine_all_team_factors() -> None:

    # calculate the final rating for all teams using the forms above
    for team in clutch_metric.get_final_rating_dict().keys():
        team_total_rating[team] = (
            (clutch_metric.get_final_rating_dict()[team] *
                team_weights['clutch_weight']) +
            (goal_differential_metric.get_final_rating_dict()[team] *
                team_weights['goal_diff_weight']) +
            (penalty_kill_metric.get_final_rating_dict()[team] *
                team_weights['penalty_kill_weight']) +
            (power_play_metric.get_final_rating_dict()[team] *
                team_weights['power_play_weight']) +
            (recent_form_metric.get_final_rating_dict()[team] *
                team_weights['recent_form_weight']) +
            (shot_differential_metric.get_final_rating_dict()[team] *
                team_weights['shot_diff_weight']) +
            (strength_of_schedule_metric.get_final_rating_dict()[team] *
                team_weights['strength_of_schedule_weight'])
        )


def scale_all_goalie_data() -> None:
    utilization_metric.scale_rating("G",
        utilization_metric.get_games_played_dict())
    apply_sigmoid_correction(utilization_metric.get_final_rating_dict("G"))

    discipline_metric.scale_rating("G",
        utilization_metric.get_final_rating_dict("G"))

    goals_against_metric.scale_rating("G",
        utilization_metric.get_final_rating_dict("G"))
    
    save_consistency_metric.scale_rating("G",
        goals_against_metric.get_games_played_dict())

    save_percentage_metric.scale_rating(
        {'game_time' : utilization_metric.get_base_rating_dict("G"),
        'pp_opertunities' : power_play_metric.get_pp_chances_dict(),
        'pk_oppertunities' : penalty_kill_metric.get_pk_chances_dict(),
        'utilization' : utilization_metric.get_final_rating_dict("G"),
        'goalie_teams' : goalie_teams}
    )


def scale_all_forward_data() -> None:
    utilization_metric.scale_rating("C",
        utilization_metric.get_games_played_dict())
    apply_sigmoid_correction(utilization_metric.get_final_rating_dict("C"))

    blocked_shots_metric.scale_rating("C",
        shot_differential_metric.get_base_rating_dict(), forward_teams)

    contributing_games_metric.scale_rating("C",
        contributing_games_metric.get_games_played_dict())

    discipline_metric.scale_rating("C",
        utilization_metric.get_final_rating_dict("C"))

    hitting_metric.scale_rating("C", hitting_metric.get_games_played_dict())

    multipoint_game_metric.scale_rating("C",
        multipoint_game_metric.get_games_played_dict())

    plus_minus_metric.scale_rating("C",
        utilization_metric.get_final_rating_dict("C"))

    total_points_metric.scale_rating("C",
        total_points_metric.get_games_played_dict())

    turnovers_metric.scale_rating("C",
        utilization_metric.get_final_rating_dict("C"))


def scale_all_defense_data() -> None:
    utilization_metric.scale_rating("D",
        utilization_metric.get_games_played_dict())
    apply_sigmoid_correction(utilization_metric.get_final_rating_dict("D"))

    blocked_shots_metric.scale_rating("D",
        shot_differential_metric.get_base_rating_dict(), defensemen_teams)

    contributing_games_metric.scale_rating("D",
        contributing_games_metric.get_games_played_dict())

    discipline_metric.scale_rating("D",
        utilization_metric.get_final_rating_dict("D"))

    hitting_metric.scale_rating("D", hitting_metric.get_games_played_dict())

    multipoint_game_metric.scale_rating("D",
        multipoint_game_metric.get_games_played_dict())

    plus_minus_metric.scale_rating("D",
        utilization_metric.get_final_rating_dict("D"))

    total_points_metric.scale_rating("D",
        total_points_metric.get_games_played_dict())

    turnovers_metric.scale_rating("D",
        utilization_metric.get_final_rating_dict("D"))
    

def run_played_game_parser_engine(game_types : str="R", game_list : dict={}):

    # loop through all gathered match dates until we have parsed all data
    sorted_date_list = sorted(game_list)

    # determine at which dates we should collate and mark trend data
    i = 1
    parsed_dates = 0
    ranking_dates = []
    all_ranking_periods = []
    ranking_period = []
    last_ranking_date = ""
    final_date = False
    for date in sorted_date_list:
        ranking_period.append(date)

        # if we are doing ranking dates based on freqency of days
        if TREND_FREQUENCY > 0:
            if i % TREND_FREQUENCY == 0:
                ranking_dates.append(date)
                all_ranking_periods.append(ranking_period)
                ranking_period = []
            elif date == sorted_date_list[-1]:
                all_ranking_periods.append(ranking_period)

        # otherwise we are doing it based on a specific day of the week
        else:
            parsed_date = date.split("-")
            parsed_date = datetime.date(int(parsed_date[0]),
                int(parsed_date[1]), int(parsed_date[2]))
            if parsed_date.weekday() == TREND_DAY:
                ranking_dates.append(date)
                all_ranking_periods.append(ranking_period)
                ranking_period = []
            elif date == sorted_date_list[-1]:
                all_ranking_periods.append(ranking_period)
        i += 1

    # we've grouped dates together by when trends should be updated to save
    # time, so now loop through those groups of ranking periods
    for ranking_period in all_ranking_periods:
        print("{} -> {}".format(ranking_period[0], ranking_period[-1]))
        update_progress_text(
            "Parsing Dates: {} to {}".format(ranking_period[0], ranking_period[-1])
        )

        # determine if this is the last date in the date list
        if ranking_period == all_ranking_periods[-1]:
            final_date = True

        # create a few match parsing processes to speed things up a bit
        subprocess_count = 32
        metric_process_list = []
        for i in range(subprocess_count):
            metric_process_list.append(Process(target=worker_node,
                args=(match_input_queue, match_output_queue))
            )
        for process in metric_process_list:
            process.start()

        # feed in matches until all those in the current date have been parsed
        run_match_parser(ranking_period, last_ranking_date, game_list)
    
        # let the metric workers know there are no more matches
        for i in range(subprocess_count):
            match_input_queue.put('STOP')
    
        # keep reading the metric output queue until all data is returned
        for i in range(subprocess_count):
            for output_list in iter(match_output_queue.get, 'STOP'):

                # check if we are getting a batch of player data or team data
                # players
                if "player_data" in output_list.keys():

                    # Goalies
                    goalie_metrics = (
                        output_list["player_data"]['goalie_metrics']
                    )
                    for metric in goalie_metrics_list:
                        metric.add_match_data(goalie_metrics[metric.name], "G")
                    for goalie in goalie_metrics['utilization'].keys():
                        goalie_teams[goalie] = (
                            goalie_metrics['utilization'][goalie]['team']
                        )

                    # Forwards
                    forward_metrics = (
                        output_list['player_data']['forward_metrics']
                    )
                    for metric in player_metrics_list:
                        metric.add_match_data(forward_metrics[metric.name], "C")
                    for forward in forward_metrics['utilization'].keys():
                        forward_teams[forward] = (
                            forward_metrics['utilization'][forward]['team']
                        )

                    # Defensemen
                    defensemen_metrics = (
                        output_list['player_data']['defensemen_metrics']
                    )
                    for metric in player_metrics_list:
                        metric.add_match_data(defensemen_metrics[metric.name],
                            "D")
                    for defenseman in defensemen_metrics['utilization'].keys():
                        defensemen_teams[defenseman] = (
                            defensemen_metrics['utilization'][defenseman][
                                'team']
                        )
                        
                elif "play_by_play_data" in output_list.keys():
                    shooting_percentage_add_match_data(
                        output_list["play_by_play_data"]["shots"],
                        output_list["play_by_play_data"]["goals"])
                        
                # teams
                else:
                    metric_data = output_list["team_data"]
                    for metric in team_metrics:
                        metric.add_match_data(metric_data[metric.name])

        for process in metric_process_list:
            process.join()

##################### TEAM RANKING PERIOD PROCESSING ###########################
        # call any cleanup calculations required
        for metric in team_metrics:
            metric.scale_rating()

        # only take the time to plot if we are done with all data
        if final_date:

            # now start the processes for plotting
            plotting_process_list = []
            for i in range(subprocess_count):
                plotting_process_list.append(Process(target=worker_node,
                    args=(plotting_queue, dummy_queue))
                )
            for process in plotting_process_list:
                process.start()

            # write out any plots before sigmoid correction
            print("Plot Team data before correction")
            plot_uncorrected_team_metrics(game_types)

        # Clutch Rating
        apply_sigmoid_correction(clutch_metric.get_final_rating_dict())

        # Goal Differential
        apply_sigmoid_correction(
            goal_differential_metric.get_final_rating_dict())

        # Penalty Kill
        apply_sigmoid_correction(
            penalty_kill_metric.get_final_rating_dict())
        
        # Power Play
        apply_sigmoid_correction(
            power_play_metric.get_final_rating_dict())

        # Recent Form
        apply_sigmoid_correction(
            recent_form_metric.get_streak_dict())
        apply_sigmoid_correction(
            recent_form_metric.get_longest_streak_dict())
        apply_sigmoid_correction(
            recent_form_metric.get_last_10_dict())
        apply_sigmoid_correction(
            recent_form_metric.get_last_20_dict())
        apply_sigmoid_correction(
            recent_form_metric.get_last_40_dict())
        apply_sigmoid_correction(recent_form_metric.get_final_rating_dict())
        
        # Shot Differential
        apply_sigmoid_correction(
            shot_differential_metric.get_final_rating_dict())

        # Strenght of Schedule
        apply_sigmoid_correction(
            strength_of_schedule_metric.get_final_rating_dict())

        # write out any plots after sigmoid correction
        if final_date:
            print("Plot Team data after correction")
            plot_corrected_team_metrics(game_types)

        # combine all factors and plot the total rankings
        combine_all_team_factors()
        
        if final_date:
            print("Plot combined team metrics")
            plot_combined_team_metrics(game_types)
            

        ### Update any trend sets if on ranking date ###
        for metric in team_metrics:
            metric.update_trend(ranking_period[-1])

        # sort teams for absolute and average rankings
        tuple_list = []
        ranking_absolutes[ranking_period[-1]] = {}
        ranking_averages[ranking_period[-1]] = {}
        for team, rating in team_total_rating.items():
            tuple_list.append(tuple((team, rating)))
        tuple_list.sort(key = lambda x: x[1], reverse=True)
        for count in range(0, len(tuple_list), 1):
            sum = 0
            ind = 1
            team = tuple_list[count][0]
            ranking_absolutes[ranking_period[-1]][team] = float(count + 1)
            for date in ranking_absolutes.keys():
                if date.find('-') == -1:
                    break
                if team in ranking_absolutes[date]:
                    sum += ranking_absolutes[date][team]
                    ind += 1
            sum /= ind
            ranking_averages[ranking_period[-1]][team] = float(sum)
        
        # final rating
        total_rating_trend[ranking_period[-1]] = {}
        for team in team_total_rating.keys():
            total_rating_trend[ranking_period[-1]][team] = \
                team_total_rating[team]

####################### PLAYER RANKING PERIOD PROCESSING #######################
        ### Goalies ###
        scale_all_goalie_data()

        ### Forwards ###
        scale_all_forward_data()

        ### Defensemen ###
        scale_all_defense_data()

        if final_date:
            plot_uncorrected_player_metrics(game_types)

        # Goalies
        apply_sigmoid_correction(discipline_metric.get_final_rating_dict("G"))
        apply_sigmoid_correction(
            goals_against_metric.get_final_rating_dict("G"), True)
        apply_sigmoid_correction(
            save_consistency_metric.get_final_rating_dict("G"))
        apply_sigmoid_correction(
            save_percentage_metric.get_final_rating_dict("G"))

        # Forwards
        apply_sigmoid_correction(
            blocked_shots_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(
            contributing_games_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(discipline_metric.get_final_rating_dict("C"),
            True)
        apply_sigmoid_correction(hitting_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(
            multipoint_game_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(plus_minus_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(total_points_metric.get_final_rating_dict("C"))
        apply_sigmoid_correction(turnovers_metric.get_final_rating_dict("C"))

        # Defensemen
        apply_sigmoid_correction(
            blocked_shots_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(
            contributing_games_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(discipline_metric.get_final_rating_dict("D"),
            True)
        apply_sigmoid_correction(hitting_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(
            multipoint_game_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(plus_minus_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(total_points_metric.get_final_rating_dict("D"))
        apply_sigmoid_correction(turnovers_metric.get_final_rating_dict("D"))

        if final_date:
            print("Plot Player data after correction")
            plot_corrected_player_metrics(game_types)

        ### combine metrics to overall score and plot ###
        # Goalies
        for goalie in utilization_metric.get_final_rating_dict("G").keys():
            goalie_total_rating[goalie] = (
                (utilization_metric.get_final_rating_dict("G")[goalie] *
                    goalie_weights['utilization_weight']) +
                (discipline_metric.get_final_rating_dict("G")[goalie] *
                    goalie_weights['discipline_weight']) +
                (goals_against_metric.get_final_rating_dict("G")[goalie] *
                    goalie_weights['goals_against_weight']) +
                (save_percentage_metric.get_final_rating_dict("G")[goalie] *
                    goalie_weights['save_percentage_weight']) +
                (save_consistency_metric.get_final_rating_dict("G")[goalie] *
                    goalie_weights['save_consitency_weight'])
            )
            goalie_total_rating[goalie] *= (1 - EYE_TEST_WEIGHT)
            if goalie in player_eye_test_rating.keys():
                goalie_total_rating[goalie] += (
                    EYE_TEST_WEIGHT * float(player_eye_test_rating[goalie])
                )
            else:
                goalie_total_rating[goalie] += (
                    goalie_total_rating[goalie] * EYE_TEST_WEIGHT
                )

        # Forwards
        for forward in utilization_metric.get_final_rating_dict("C").keys():
            forward_total_rating[forward] = (
                (hitting_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['hits_weight']) +
                (blocked_shots_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['shot_blocking_weight']) +
                (utilization_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['utilization_weight']) +
                (discipline_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['discipline_weight']) +
                (plus_minus_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['plus_minus_weight']) +
                (total_points_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['points_weight']) +
                (turnovers_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['takeaways_weight']) +
                (contributing_games_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['contribution_weight']) +
                (multipoint_game_metric.get_final_rating_dict("C")[forward] *
                    forward_weights['multipoint_weight'])
            )
            forward_total_rating[forward] *= (1 - EYE_TEST_WEIGHT)
            if forward in player_eye_test_rating.keys():
                forward_total_rating[forward] += (
                    EYE_TEST_WEIGHT * float(player_eye_test_rating[forward])
                )
            else:
                forward_total_rating[forward] += (
                    forward_total_rating[forward] * EYE_TEST_WEIGHT
                )
            
        # Defense
        for defensemen in utilization_metric.get_final_rating_dict("D").keys():
            defensemen_total_rating[defensemen] = (
                (hitting_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['hits_weight']) +
                (blocked_shots_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['shot_blocking_weight']) +
                (utilization_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['utilization_weight']) +
                (discipline_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['discipline_weight']) +
                (plus_minus_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['plus_minus_weight']) +
                (total_points_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['points_weight']) +
                (turnovers_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['takeaways_weight']) +
                (contributing_games_metric.get_final_rating_dict("D")[
                    defensemen] * defenseman_weights['contribution_weight']) +
                (multipoint_game_metric.get_final_rating_dict("D")[defensemen] *
                    defenseman_weights['multipoint_weight'])
            )
            defensemen_total_rating[defensemen] *= (1 - EYE_TEST_WEIGHT)
            if defensemen in player_eye_test_rating.keys():
                defensemen_total_rating[defensemen] += (
                    EYE_TEST_WEIGHT * float(player_eye_test_rating[defensemen])
                )
            else:
                defensemen_total_rating[defensemen] += (
                    defensemen_total_rating[defensemen] * EYE_TEST_WEIGHT
                )
        if final_date:
            plot_combined_player_metrics(game_types)

        # now update the last ranking date to indicate we have new trends
        last_ranking_date = ranking_period[-1]

############################# END POST PROCESSING ##############################
        # Print out trend files
        if final_date:

            ############## TEAMS ##############
            plot_trend_team_metrics(game_types)
            
            ################ PLAYERS ###############
            # sort players into team rosters
            ### Goalies ###
            i = 1
            sorted_goalies = \
                dict(sorted(goalie_total_rating.items(),
                    key=lambda item: item[1], reverse=True))
            average_player_rating.clear()
            average_goalie_rating.clear()
            for goalie in sorted_goalies:

                # Get the team for this player
                goalie_team = goalie_teams[goalie]

                # if the team already has some players listed, just add this
                # player
                if goalie_team in average_goalie_rating.keys():

                    # only account for top 3 starters
                    if average_goalie_rating[goalie_team][1] < 3:
                        average_goalie_rating[goalie_team][0] += i
                        average_goalie_rating[goalie_team][1] += 1
                else:
                    average_goalie_rating[goalie_team] = [i, 1]
                i += 1

            # now loop through the teams and add to team player rankings
            for team in average_goalie_rating:
                if team in average_player_rating.keys():
                    average_player_rating[team][0] += \
                        average_goalie_rating[team][0]
                    average_player_rating[team][1] += \
                        average_goalie_rating[team][1]
                else:
                    average_player_rating[team] = [
                        average_goalie_rating[team][0],
                        average_goalie_rating[team][1]
                    ]

                # calculate goalie average
                average_goalie_rating[team] = (
                    average_goalie_rating[team][0] /
                        average_goalie_rating[team][1])
            
            
            ### Forwards ###
            i = 1
            sorted_forward = \
                dict(sorted(forward_total_rating.items(),
                    key=lambda item: item[1], reverse=True))
            average_forward_rating.clear()
            for forward in sorted_forward:

                # Get the team for this player
                forward_team = forward_teams[forward]

                # if the team already has some players listed, just add this
                # player
                if forward_team in average_forward_rating.keys():

                    # only account for top 12 starters
                    if average_forward_rating[forward_team][1] < 13:
                        average_forward_rating[forward_team][0] += i
                        average_forward_rating[forward_team][1] += 1
                else:
                    average_forward_rating[forward_team] = [i, 1]
                i += 1

            # now loop through the teams and add to team player rankings
            for team in average_forward_rating:
                if team in average_player_rating.keys():
                    average_player_rating[team][0] += \
                        average_forward_rating[team][0]
                    average_player_rating[team][1] += \
                        average_forward_rating[team][1]
                else:
                    average_player_rating[team] = [
                        average_forward_rating[team][0],
                        average_forward_rating[team][1]
                    ]

                # calculate forward average
                average_forward_rating[team] = (
                    average_forward_rating[team][0] /
                        average_forward_rating[team][1])
            
            
            ### Defensemen ###
            i = 1
            sorted_defenseman = \
                dict(sorted(defensemen_total_rating.items(),
                    key=lambda item: item[1], reverse=True))
            average_defenseman_rating.clear()
            for defenseman in sorted_defenseman:
                
                # Get the team for this player
                defenseman_team = defensemen_teams[defenseman]

                # if the team already has some players listed, just add this
                # player
                if defenseman_team in average_defenseman_rating.keys():

                    # only add the player if he is in the top 6 defensemen
                    if average_defenseman_rating[defenseman_team][1] < 7:
                        average_defenseman_rating[
                            defenseman_team][0] += i
                        average_defenseman_rating[
                            defenseman_team][1] += 1
                else:
                    average_defenseman_rating[defenseman_team] = [i, 1]
                i += 1

            # now loop through the teams and add to team player rankings
            for team in average_defenseman_rating:
                if team in average_player_rating.keys():
                    average_player_rating[team][0] += \
                        average_defenseman_rating[team][0]
                    average_player_rating[team][1] += \
                        average_defenseman_rating[team][1]
                else:
                    average_player_rating[team] = [
                        average_defenseman_rating[team][0],
                        average_defenseman_rating[team][1]
                    ]

                # calculate the defensemen average
                average_defenseman_rating[team] = \
                    average_defenseman_rating[team][0] / \
                        average_defenseman_rating[team][1]
            
            ### All Roles ###
            for team in average_player_rating:
                average_player_rating[team] = average_player_rating[team][0] / \
                    average_player_rating[team][1]
            
            # now plot all averge player metrics
            plot_average_player_team_metrics(game_types)
        parsed_dates += 1
        update_progress_bar((parsed_dates / len(all_ranking_periods))*100)

    # if the end of regular season add to year on year summaries
    if REG_SEASON_COMPLETE and final_date:

        ############## TEAMS ################
        header_row = True
        row_list = []
        if game_types == "R":
            prefix = "Reg_Season_"
        else:
            prefix = "Post_Season_"

        # open the total rating file for all teams and copy out the data
        with open("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
                "TotalRating.csv",
            'r', newline='', encoding='utf-16') as csv_read_file:
            csv_reader = csv.reader(csv_read_file, delimiter='\t',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                if header_row:
                    header_row = False
                    continue
                row_list.append(row)
        csv_read_file.close()

        # now rewrite the data to a year on year trend file with extra headers
        with open(
            "Output_Files\Team_Files\Trend_Files\TeamYearlyRanking.csv",
            'a+', newline='', encoding='utf-16') as csv_write_file:
            csv_writer = csv.writer(csv_write_file, delimiter=',',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in row_list:
                writeout = [str(SEASON)[0:4] + "-" + str(SEASON)[4:]]
                writeout.append(row[0])
                writeout.append(divisions[row[0]])
                writeout.append(row[1])
                csv_writer.writerow(writeout)
        csv_write_file.close()

        # plot the updated year on year data
        plotting_queue.put((plot_team_trend_set,
            ("Output_Files\Team_Files\Trend_Files\TeamYearlyRanking.csv",
            ["Season", "Rating Score"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Final_Rating_Score/year_on_year_score.png")))
        
        ################ PLAYERS ##############
        ### Goalies
        header_row = True
        row_list = []        

        # open the total rating file for all teams and copy out the data
        print("Reading Out Goalie Total File")
        with open(
            "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
                "Goalie_Total_Rating.csv",
            'r', newline='', encoding='utf-16') as csv_read_file:
            csv_reader = csv.reader(csv_read_file, delimiter='\t',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                if header_row:
                    header_row = False
                    continue
                row_list.append(row)
                if len(row_list) == 10:
                    break
        csv_read_file.close()

        # now rewrite the data to a year on year trend file with extra headers
        print("Writing Out Goalie Updates")
        with open(
            "Output_Files\Goalie_Files\Trend_Files\GoalieYearlyRanking.csv",
            'a+', newline='', encoding='utf-16') as csv_write_file:
            csv_writer = csv.writer(csv_write_file, delimiter=',',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in row_list:
                writeout = [str(SEASON)[0:4] + "-" + str(SEASON)[4:]]
                writeout.append(
                    row[0].split(" ")[1] + " " + row[0].split(" ")[2])
                writeout.append(row[2])
                writeout.append(row[1])
                csv_writer.writerow(writeout)
        csv_write_file.close()

        # plot the updated year on year data
        plotting_queue.put((plot_player_trend_set,
            ("Output_Files\Goalie_Files\Trend_Files\GoalieYearlyRanking.csv",
            ["Season", "Total Rating", "Goalie"], 0.0, 0.0, sigmoid_ticks,
            "Graphs/Goalies/Goalie_Total_Rating/year_on_year_score.png")))
        
        ### Forwards
        header_row = True
        row_list = []        

        # open the total rating file for all teams and copy out the data
        print("Reading Out Forward Total File")
        with open(
            "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
                "Forward_Total_Rating.csv",
            'r', newline='', encoding='utf-16') as csv_read_file:
            csv_reader = csv.reader(csv_read_file, delimiter='\t',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                if header_row:
                    header_row = False
                    continue
                row_list.append(row)
                if len(row_list) == 10:
                    break
        csv_read_file.close()

        # now rewrite the data to a year on year trend file with extra headers
        print("Writing Out Forward Updates")
        with open(
            "Output_Files\Forward_Files\Trend_Files\ForwardYearlyRanking.csv",
            'a+', newline='', encoding='utf-16') as csv_write_file:
            csv_writer = csv.writer(csv_write_file, delimiter=',',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in row_list:
                writeout = [str(SEASON)[0:4] + "-" + str(SEASON)[4:]]
                writeout.append(
                    row[0].split(" ")[1] + " " + row[0].split(" ")[2])
                writeout.append(row[2])
                writeout.append(row[1])
                csv_writer.writerow(writeout)
        csv_write_file.close()

        # plot the updated year on year data
        plotting_queue.put((plot_player_trend_set,
            ("Output_Files\Forward_Files\Trend_Files\ForwardYearlyRanking.csv",
            ["Season", "Total Rating", "Forward"], 0.0, 0.0, sigmoid_ticks,
            "Graphs/Forward/Forward_Total_Rating/year_on_year_score.png")))
        
        ### Defensemen
        header_row = True
        row_list = []        

        # open the total rating file for all teams and copy out the data
        print("Reading Out Defensemen Total File")
        with open(
            "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
                "Defensemen_Total_Rating.csv",
            'r', newline='', encoding='utf-16') as csv_read_file:
            csv_reader = csv.reader(csv_read_file, delimiter='\t',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                if header_row:
                    header_row = False
                    continue
                row_list.append(row)
                if len(row_list) == 10:
                    break
        csv_read_file.close()

        # now rewrite the data to a year on year trend file with extra headers
        print("Writing Out Defensemen Updates")
        with open(
            "Output_Files\Defensemen_Files\Trend_Files" +
                "\DefensemenYearlyRanking.csv",
            'a+', newline='', encoding='utf-16') as csv_write_file:
            csv_writer = csv.writer(csv_write_file, delimiter=',',
                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in row_list:
                writeout = [str(SEASON)[0:4] + "-" + str(SEASON)[4:]]
                writeout.append(
                    row[0].split(" ")[1] + " " + row[0].split(" ")[2])
                writeout.append(row[2])
                writeout.append(row[1])
                csv_writer.writerow(writeout)
        csv_write_file.close()

        # plot the updated year on year data
        plotting_queue.put((plot_player_trend_set,
            ("Output_Files\Defensemen_Files\Trend_Files" +
                "\DefensemenYearlyRanking.csv",
            ["Season", "Total Rating", "Defenseman"], 0.0, 0.0, sigmoid_ticks,
            "Graphs/Defensemen/Defensemen_Total_Rating/year_on_year_score.png")
        ))
        
    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(subprocess_count):
        plotting_queue.put('STOP')
    for process in plotting_process_list:
        process.join()

    # remove all the instance files to save clutter
    # for dir in \
    #     os.walk(os.getcwd() + "\Output_Files\Team_Files\Instance_Files"):
    #     for file in dir[2]:
    #         os.remove(os.getcwd() +
    #             "\Output_Files\Team_Files\Instance_Files\\" + file)
    # for dir in \
    #     os.walk(os.getcwd() + "\Output_Files\Goalie_Files\Instance_Files"):
    #     for file in dir[2]:
    #         os.remove(os.getcwd() +
    #             "\Output_Files\Goalie_Files\Instance_Files\\" + file)
    # for dir in \
    #     os.walk(os.getcwd() + "\Output_Files\Forward_Files\Instance_Files"):
    #     for file in dir[2]:
    #         os.remove(os.getcwd() +
    #             "\Output_Files\Forward_Files\Instance_Files\\" + file)
    # for dir in \
    #     os.walk(os.getcwd() +
    #         "\Output_Files\Defensemen_Files\Instance_Files"):
    #     for file in dir[2]:
    #         os.remove(os.getcwd() +
    #             "\Output_Files\Defensemen_Files\Instance_Files\\" + file)
            

def calculate_metric_share(home_rating, away_rating) -> list:
    rating_total = home_rating + away_rating
    try:
        # print("Home Rating : ", home_rating, " - Away Rating : ", away_rating)
        # print("Home Share : ", home_rating / rating_total, " - Away Share : ",
            # away_rating / rating_total)
        return [home_rating / rating_total, away_rating / rating_total]
    except ZeroDivisionError:
        print("Home Share : ", 0.5, " - Away Share : ", 0.5)
        return [0.5, 0.5]


def calculate_series_predictions(game_types : str="",
    total_home_rating : float=0.0, total_away_rating : float=0.0,
    home_team : str="", away_team : str="") -> None:

    # for any series which is not a 4-0, we must subtract the cases where
    # the losing team would win the last game, as those possbilities could never
    # actually happen. i.e we are not playing 7 random games and calculating the
    # odds of winning 4 which would be the basic (n choose k) we are instead
    # doing a special case were the 4th win by either team ends the set
    # print("Base Odds:\n\t{} - {}\n\t{} - {}".format(
    #     home_team, total_home_rating, away_team, total_away_rating))
    
    # if its a regular season game just calculate base odds
    if game_types == "R":
        return
    
    # first calculate the 4-0 odds for either team
    home_odds = total_home_rating**4
    away_odds = total_away_rating**4
    print("4-0 Odds:\n\t{} - {}\n\t{} - {}".format(home_team, home_odds,
        away_team, away_odds))
    
    # calculate 4-1 odds
    five_choose_four = 5 - 1
    home_odds = (
        five_choose_four * (total_home_rating**4) * (total_away_rating**1)
    )
    away_odds = (
        five_choose_four * (total_away_rating**4) * (total_home_rating*1)
    )
    print("4-1 Odds:\n\t{} - {}\n\t{} - {}".format(home_team, home_odds,
        away_team, away_odds))

    # calculate 4-2 odds
    six_choose_four = 15 - 5
    home_odds = (
        six_choose_four * (total_home_rating**4) * (total_away_rating**2)
    )
    away_odds = (
        six_choose_four * (total_away_rating**4) * (total_home_rating**2)
    )
    print("4-2 Odds:\n\t{} - {}\n\t{} - {}".format(home_team, home_odds,
        away_team, away_odds))

    # calculate 4-3 odds
    seven_choose_four = 35 - 15
    home_odds = (
        seven_choose_four * (total_home_rating**4) * (total_away_rating**3)
    )
    away_odds = (
        seven_choose_four * (total_away_rating**4) * (total_home_rating**3)
    )
    print("4-3 Odds:\n\t{} - {}\n\t{} - {}".format(home_team, home_odds,
        away_team, away_odds))


def run_upcoming_game_parser_engine(game_types : str="R", game_list : dict={})\
                                                                        -> None:

    # loop through all gathered match dates until we have parsed all data
    final_team_ratings = {}

    # For now only parse the next 7 days of games because its too much damn data
    count = 7
    for date in game_list.keys():
        if count < 1:
            break
        for match in game_list[date]:
            away_team = match["game_stats"]["away_team"]
            home_team = match["game_stats"]["home_team"]
            match_key = "{}: {} vs. {}".format(date, home_team, away_team)
            print(match_key)

            # some error catching for missing stats
            # Clutch Rating
            if home_team not in clutch_metric.get_final_rating_dict().keys():
                home_stat = 0
            else:
                home_stat = clutch_metric.get_final_rating_dict()[home_team]
            if away_team not in clutch_metric.get_final_rating_dict().keys():
                away_stat = 0
            else:
                away_stat = clutch_metric.get_final_rating_dict()[away_team]
            clutch_ratings = calculate_metric_share(home_stat, away_stat)

            # Goal Differential
            if home_team not in goal_differential_metric.get_final_rating_dict(
                ).keys():

                home_stat = 0
            else:
                home_stat = (
                    goal_differential_metric.get_final_rating_dict()[home_team]
                )
            if away_team not in goal_differential_metric.get_final_rating_dict(
                ).keys():

                away_stat = 0
            else:
                away_stat = (
                    goal_differential_metric.get_final_rating_dict()[away_team]
                )
            goal_differential_ratings = calculate_metric_share(home_stat,
                away_stat)

            # Penalty Kill
            if home_team not in penalty_kill_metric.get_final_rating_dict(
                ).keys():

                home_stat = 0
            else:
                home_stat = (
                    penalty_kill_metric.get_final_rating_dict()[home_team]
                )
            if away_team not in penalty_kill_metric.get_final_rating_dict(
                ).keys():

                away_stat = 0
            else:
                away_stat = (
                    penalty_kill_metric.get_final_rating_dict()[away_team]
                )
            penalty_kill_ratings = calculate_metric_share(home_stat, away_stat)

            # Power Play
            if home_team not in power_play_metric.get_final_rating_dict(
                ).keys():

                home_stat = 0
            else:
                home_stat = (
                    power_play_metric.get_final_rating_dict()[home_team]
                )
            if away_team not in power_play_metric.get_final_rating_dict(
                ).keys():

                away_stat = 0
            else:
                away_stat = (
                    power_play_metric.get_final_rating_dict()[away_team]
                )
            power_play_ratings = calculate_metric_share(home_stat, away_stat)

            # Recent Form
            if home_team not in recent_form_metric.get_final_rating_dict(
                ).keys():

                home_stat = 0
            else:
                home_stat = (
                    recent_form_metric.get_final_rating_dict()[home_team]
                )
            if away_team not in recent_form_metric.get_final_rating_dict(
                ).keys():

                away_stat = 0
            else:
                away_stat = (
                    recent_form_metric.get_final_rating_dict()[away_team]
                )
            recent_form_ratings = calculate_metric_share(home_stat, away_stat)

            # Shot Differential
            if home_team not in shot_differential_metric.get_final_rating_dict(
                ).keys():

                home_stat = 0
            else:
                home_stat = (
                    shot_differential_metric.get_final_rating_dict()[home_team]
                )
            if away_team not in shot_differential_metric.get_final_rating_dict(
                ).keys():

                away_stat = 0
            else:
                away_stat = (
                    shot_differential_metric.get_final_rating_dict()[away_team]
                )
            shot_differential_ratings = calculate_metric_share(home_stat,
                away_stat)

            # Strength of Schedule
            if (home_team not in strength_of_schedule_metric.get_final_rating_dict().keys()):
                home_stat = 0
            else:
                home_stat = (
                    strength_of_schedule_metric.get_final_rating_dict()[home_team]
                )
            if (away_team not in strength_of_schedule_metric.get_final_rating_dict().keys()):
                away_stat = 0
            else:
                away_stat = (
                    strength_of_schedule_metric.get_final_rating_dict()[away_team]
                )
            strength_of_schedule_ratings = calculate_metric_share(home_stat,
                away_stat)
            
            # Player rankings will exist if team has played at all no need for
            # extra checking here (I hope)
            # Because these are averages and not the scaled metrics, we actually
            # want to swap home and away such that the better (lower) team gets
            # the larger portion of the share
            goalie_average_ratings = calculate_metric_share(
                average_goalie_rating[away_team],
                average_goalie_rating[home_team])
            forward_average_ratings = calculate_metric_share(
                average_forward_rating[away_team],
                average_forward_rating[home_team])
            defenseman_average_ratings = calculate_metric_share(
                average_defenseman_rating[away_team],
                average_defenseman_rating[home_team])
            
            team_total_ratings = calculate_metric_share(
                team_total_rating[home_team], team_total_rating[away_team])
            
            # Combine all ratings into final set
            final_team_ratings[match_key] = [(
                (team_total_ratings[0] * 0.70) +
                ((
                    (goalie_average_ratings[0] * 0.30) +
                    (forward_average_ratings[0] * 0.30) +
                    (defenseman_average_ratings[0] * 0.40)
                ) * 0.30)
            ),
            (
                (team_total_ratings[1] * 0.70) +
                ((
                    (goalie_average_ratings[1] * 0.30) +
                    (forward_average_ratings[1] * 0.30) +
                    (defenseman_average_ratings[1] * 0.40)
                ) * 0.30)
            ),
                clutch_ratings[0], clutch_ratings[1],
                goal_differential_ratings[0], goal_differential_ratings[1],
                penalty_kill_ratings[0], penalty_kill_ratings[1],
                power_play_ratings[0], power_play_ratings[1],
                recent_form_ratings[0], recent_form_ratings[1],
                shot_differential_ratings[0], shot_differential_ratings[1],
                strength_of_schedule_ratings[0],
                    strength_of_schedule_ratings[1],
                goalie_average_ratings[0], goalie_average_ratings[1],
                forward_average_ratings[0], forward_average_ratings[1],
                defenseman_average_ratings[0], defenseman_average_ratings[1],
            ]
        count -= 1

    # run though matches and parse out team names to graph properly
    calculated_matches = []
    for match in final_team_ratings.keys():
        file_name = match.replace(" ", "_")
        file_name = file_name.replace(":","")
        file_name = file_name.replace(".","")
        team_names = file_name
        for char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']:
            team_names = team_names.replace(char, "")
        team_names = team_names.split("vs")
        team_names[0] = team_names[0].replace("_", "", 1)
        team_names[0] = team_names[0].replace("_", " ")
        team_names[0] = team_names[0][0:-1]
        team_names[1] = team_names[1].replace("_", "", 1)
        team_names[1] = team_names[1].replace("_", " ")

        # only bother graphing and doing odds if we have not run this match
        # before
        # TODO make this condition only for post season where series exist
        # in the regular season odds will change more between games and should
        # be rerun each time
        if ((team_names[0] + "_vs_" + team_names[1]) 
                not in calculated_matches) and \
            ((team_names[1] + "_vs_" + team_names[0]) 
                not in calculated_matches):
            calculated_matches.append(team_names[0] + "_vs_" + team_names[1])

            # calculate the odds for different types of series wins
            # TODO this only needs to be run for playoff series. The basic
            # calculations by calculate_metric_share will do single game odds
            calculate_series_predictions(
                game_types, final_team_ratings[match][0],
                final_team_ratings[match][1], team_names[0], team_names[1]
            )
            odds_list = "{:.2f}".format(1 / final_team_ratings[match][0]) + \
                " : " + "{:.2f}".format(1 / final_team_ratings[match][1])
            write_out_matches_file(
                "Output_Files/Team_Files/Trend_Files/{}.csv".format(file_name),
                ["Rating", "Home Odds", "Away Odds"],
                ["Total", "Clutch", "Goal Differential", "Penalty Kill",
                    "Power Play", "Recent Form", "Shot Differential",
                    "Strenght of Schedule", "Goalie Rating", "Forward Rating",
                    "Defenseman Rating"],
                final_team_ratings[match])
            plot_matches_ranking(
                "Output_Files/Team_Files/Trend_Files/{}.csv".format(file_name),
                [team_names[0], team_names[1]], sigmoid_ticks,
                "Graphs/Teams/Matches/{}.png".format(file_name), odds_list)
            

def gather_match_records():
    
    # get all the match data
    add_progress_frame()
    update_progress_text("Gathering All Match Data: ")
    match_data_start = time.time()
    print("Gathering All Match Data")
    match_tuple = get_game_records(SEASON)
    for key in match_tuple[0].keys():
        regular_season_matches[key] = match_tuple[0][key]
    for key in match_tuple[1].keys():
        upcoming_matches[key] = match_tuple[1][key]
    for key in match_tuple[2].keys():
        playoff_matches[key] = match_tuple[2][key]
    for key in match_tuple[3].keys():
        upcoming_playoff_matches[key] = match_tuple[3][key]
    print_time_diff(match_data_start, time.time())
    close_progress_frame()


def run_main_engine():   
    start = time.time()
    freeze_support()

    eye_test_file_name = get_widget('eye-test-entry').get()
    if (parse_eye_test_file(eye_test_file_name)):
        display_error_window("Invalid Eye Test File Path", -1)
        return

    # automatically determine if the season is over based on the number of
    # unplayed matched found
    if len(upcoming_matches) == 0:
        print("Season Complete, Adding End Year Rankings\n")
        REG_SEASON_COMPLETE = True

    # if regular season games have been played then run post processing on those
    if len(regular_season_matches) > 0:
        add_progress_frame()
        update_progress_text("Running Regular Season Match Engine: ")
        print("Running Regular Season Post Process\n")
        run_played_game_parser_engine("R", regular_season_matches)
        close_progress_frame()
    print_time_diff(start, time.time())

    # upcoming match parser
    if len(upcoming_matches) > 0:
        print("Running Regular Season Match Predicter")
        run_upcoming_game_parser_engine("R", upcoming_matches)
    print_time_diff(start, time.time())

    # upcoming playoff games based on regular season for sample size reasons
    if len(upcoming_playoff_matches) > 0:
        print("Running Post Season Match Predicter")
        run_upcoming_game_parser_engine("P", upcoming_playoff_matches)
    print_time_diff(start, time.time())

    # reset all stats to just isolate post season.
    for metric in team_metrics:
        metric.reset_ratings()

    blocked_shots_metric.reset_ratings()
    contributing_games_metric.reset_ratings()
    discipline_metric.reset_ratings()
    hitting_metric.reset_ratings()
    multipoint_game_metric.reset_ratings()
    plus_minus_metric.reset_ratings()
    utilization_metric.reset_ratings()
    total_points_metric.reset_ratings()
    turnovers_metric.reset_ratings()

    goals_against_metric.reset_ratings()
    save_consistency_metric.reset_ratings()
    save_percentage_metric.rating_reset()

    team_total_rating.clear()
    goalie_total_rating.clear()
    forward_total_rating.clear()
    defensemen_total_rating.clear()

    goalie_teams.clear()
    forward_teams.clear()
    defensemen_teams.clear()

    REG_SEASON_COMPLETE = False

    # if playoffs have started then run post processing on those games
    if len(playoff_matches) > 0 :
        print(len(playoff_matches))
        print("Running Post Season Post Process\n")
        run_played_game_parser_engine("P", playoff_matches)

    # if there are matches in the schedule that are still upcoming then process
    print_time_diff(start, time.time())
    start = time.time()

if __name__ == "__main__":
    REG_SEASON_COMPLETE = False
    TREND_FREQUENCY = 0
    TREND_DAY = 5
    SEASON = 20242025

    # construct the main GUI window
    main_window = get_main_window()
    height=main_window.winfo_screenheight()/2
    width=main_window.winfo_screenwidth()/2
    main_window.geometry('{}x{}'.format(int(width), int(height)))

    # create the main welcome frame
    construct_main_menu(gather_match_records, run_main_engine)
    tk.mainloop()
