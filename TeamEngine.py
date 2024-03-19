from multiprocessing import Process, Queue, freeze_support
import requests
import json
import time
import os
import csv
import datetime
from enum import Enum

# import all custom team modules for statistical analysis
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_rating_get_trend_dict, clutch_rating_reset, \
    clutch_calculate_lead_protection, clutch_add_match_data, \
    clutch_rating_scale_by_game, clutch_update_trend
from Team_Metrics.Defensive_Rating import defensive_rating_get_dict, \
    defensive_rating_get_shots_against_dict, \
    defensive_rating_get_unscaled_shots_against_dict, \
    defensive_rating_get_goals_against_dict, defensive_rating_get_pk_dict, \
    defensive_rating_get_trend_dict, defensive_rating_get_pk_oppertunities_dict, \
    defensive_rating_reset, defensive_rating_get_data_set, \
    defensive_rating_add_match_data, defensive_rating_calculate_all, \
    defensive_rating_combine_metrics, defensive_rating_update_trends
from Team_Metrics.Offensive_Rating import offensive_rating_get_dict, \
    offensive_rating_get_shots_for_dict, offensive_rating_get_goals_for_dict, \
    offensive_rating_get_pp_dict, offensive_rating_get_trend_dict, \
    offensive_rating_get_pp_oppertunities_dict, offensive_rating_reset, \
    offensive_rating_get_data_set, offensive_rating_add_match_data, \
    offensive_rating_calculate_power_play, offensive_rating_combine_metrics, \
    offensive_rating_update_trends
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_get_streak_dict, recent_form_get_last_10_dict, \
    recent_form_get_last_20_dict, recent_form_get_last_40_dict, \
    recent_form_get_trend_dict, recent_form_reset, recent_form_get_data_set, \
    recent_form_add_match_data, recent_form_calculate_all, \
    recent_form_combine_metrics, recent_form_update_trends
from Team_Metrics.Strength_of_Schedule import strength_of_schedule_get_dict, \
    strength_of_schedule_get_games_played_dict, \
    strength_of_schedule_get_trend_dict, strength_of_schedule_reset, \
    strength_of_schedule_get_data_set, strength_of_schedule_add_match_data, \
    strength_of_schedule_scale_by_game, strength_of_schedule_update_trends

# import all custom player modules for statistical analysis
from Shared_Metrics.Utilization import utilization_base_get_dict, \
    utilization_rating_get_dict, utilization_reset, utilization_get_data_set, \
    utilization_add_match_data, utilization_scale_by_game
from Shared_Metrics.Blocked_Shots import blocks_base_get_dict, \
    blocks_rating_get_dict, blocks_reset, blocks_get_data_set, \
    blocks_add_match_data, blocks_scale_by_shots_against

### GOALIES
from Goalie_Metrics.Goalie_Goals_Against import goalie_goals_against_get_dict, \
    goalie_goals_against_reset, goalie_goals_against_get_data_set, \
    goalie_goals_against_add_match_data, \
    goalie_goals_against_scale_by_utilization
from Goalie_Metrics.Goalie_Save_Consistency import \
    goalie_save_consistency_get_dict, goalie_save_consistency_reset, \
    goalie_save_consistency_get_data_set, \
    goalie_save_consistency_add_match_data, \
    goalie_save_consistency_scale_by_games
from Goalie_Metrics.Goalie_Save_Percentage import \
    goalie_save_percentage_get_dict, goalie_save_percentage_reset, \
    goalie_save_percentage_get_data_set, goalie_save_percentage_add_match_data, \
    goalie_save_percentage_calculate_all, goalie_save_percentage_combine_metrics

### FORWARDS
from Forward_Metrics.Forward_Contributing_Games import \
    forward_contributing_games_get_dict, forward_contributing_games_reset, \
    forward_contributing_games_get_data_set, \
    forward_contributing_games_add_match_data, \
    forward_contributing_games_scale_by_games
from Forward_Metrics.Forward_Discipline import \
    forward_discipline_get_dict, forward_discipline_reset, \
    forward_discipline_get_data, forward_discipline_add_match_data, \
    forward_discipline_scale_by_utilization
from Forward_Metrics.Forward_Hits import \
    forward_hits_get_dict, forward_hits_reset, forward_hits_get_data_set, \
    forward_hits_add_match_data, forward_hits_scale_by_games
from Forward_Metrics.Forward_Multipoint_Games import \
    forward_multipoint_games_get_dict, forward_multipoint_games_reset, \
    forward_multipoint_games_get_data_set, \
    forward_multipoint_games_add_match_data, \
    forward_multipoint_games_scale_by_games
from Forward_Metrics.Forward_PlusMinus import \
    forward_plus_minus_get_dict, forward_plus_minus_reset, \
    forward_plus_minus_get_data_set, forward_plus_minus_add_match_data, \
    forward_plus_minus_scale_by_utilization
from Forward_Metrics.Forward_Takeaways import \
    forward_takeaways_get_dict, forward_takeaways_reset, \
    forward_takeaways_get_data_set, forward_takeaways_add_match_data, \
    forward_takeaways_scale_by_utilization
from Forward_Metrics.Forward_Total_Points import \
    forward_points_get_dict, forward_points_reset, forward_points_get_data_set, \
    forward_points_add_match_data, forward_points_scale_by_games


### DEFENSEMEN
from Defensemen_Metrics.Defensemen_Discipline import \
    defensemen_discipline_get_dict, defensemen_discipline_reset, \
    defensemen_discipline_get_data, defensemen_discipline_add_match_data, \
    defensemen_discipline_scale_by_utilization
from Defensemen_Metrics.Defensemen_Hits import \
    defensemen_hits_get_dict, defensemen_hits_reset, \
    defensemen_hits_get_data_set, defensemen_hits_add_match_data, \
    defensemen_hits_scale_by_games
from Defensemen_Metrics.Defensemen_PlusMinus import \
    defensemen_plus_minus_get_dict, defensmen_plus_minus_reset, \
    defensemen_plus_minus_get_data_set, defensemen_plus_minus_add_match_data, \
    defensemen_plus_minus_scale_by_utilization
from Defensemen_Metrics.Defensemen_Points import \
    defensemen_points_get_dict, defensemen_points_reset, \
    defensemen_points_get_data_set, defensemen_points_add_match_data, \
    defensemen_points_scale_by_games
from Defensemen_Metrics.Defensemen_Takeaways import \
    defensemen_takeaways_get_dict, defensemen_takeaways_reset, \
    defensemen_takeaways_get_data_set, defensemen_takeaways_add_match_data, \
    defensemen_takeaways_scale_by_utilization


# shared engine tools
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import total_rating_weights, goalie_rating_weights, \
    forward_rating_weights, defensemen_rating_weights, divisions, \
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

regular_season_matches = {}

playoff_matches = {}

upcoming_matches = {}

upcoming_playoff_matches = {}

goalie_teams = {}

forward_teams = {}

defensemen_teams = {}

player_eye_test_rating = {}

match_input_queue = Queue()
match_output_queue = Queue()
plotting_queue = Queue()
dummy_queue = Queue()


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


def print_time_diff(start_time : float=0.0, end_time : float=0.0) -> None:
    print("Completed in {} seconds".format(end_time - start_time))


def parse_eye_test_file(file_name : str="") -> None:
    with open(file_name, "r", newline='', encoding='utf-16') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            player_eye_test_rating[row[0]] = row[1]


def parse_play_by_play_penalties(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # commited penalties
    if "committedByPlayerId" in play["details"].keys():
        if play["details"]["committedByPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
        elif play["details"]["committedByPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
        else:
            print("Penalties Commited Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["committedByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # drawn penalties
    if "drawnByPlayerId" in play["details"].keys():
        if play["details"]["drawnByPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]

        elif play["details"]["drawnByPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]
        
        else:
            print("Penalties Drawn By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["drawnByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_hits(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # hits delivered
    if play["details"]["hittingPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
    elif play["details"]["hittingPlayerId"] in \
        game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
    else:
        print("Hits Delivered By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hittingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())

    # hits taken
    if play["details"]["hitteePlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
    elif play["details"]["hitteePlayerId"] in \
        game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
    else:
        print("Hits Recieved By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hitteePlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_takeaways_and_giveaways(home_team : str="", 
    away_team : str="", play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # takeaways
    if play_type == "takeaway":
        if play["details"]["playerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["takeaways"] += 1
        elif play["details"]["playerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["takeaways"] += 1
        else:
            print("Takeaway By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["playerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # giveaways
    if play_type == "giveaway":
        if play["details"]["playerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        elif play["details"]["playerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        else:
            print("Giveawayw By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["playerId"])
            print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_shots(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # blocked shots
    if play_type == "blocked-shot":

        # shots blocked
        if play["details"]["blockingPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["blockingPlayerId"]]\
                ["blocks"] += 1
        elif play["details"]["blockingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["blockingPlayerId"]]\
                ["blocks"] += 1
        else:
            print("Shot-Block By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["blockingPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

        # own shots blocked
        if play["details"]["shootingPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["blocked_shots"] += 1
        elif play["details"]["shootingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["blocked_shots"] += 1
        else:
            print("Own Shot Blocked By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["shootingPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    
    # missed shot
    if play_type == "missed-shot":
        if play["details"]["shootingPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["missed_shots"] += 1
        elif play["details"]["shootingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["missed_shots"] += 1
        else:
            print("Missed Shot By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["shootingPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
            
    if play_type == "shot-on-goal":
        if play["details"]["shootingPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["shots_on_goal"] += 1
        elif play["details"]["shootingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["shootingPlayerId"]]\
                ["shots_on_goal"] += 1
        else:
            print("Shot By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["shootingPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_faceoffs(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # losing player just gets an attempts
    if play["details"]["losingPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]\
            ["faceoff_attempts"] += 1
    elif play["details"]["losingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]\
            ["faceoff_attempts"] += 1
    else:
        print("Faceoff Lost By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["shootingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
        
    # winning player gets a win and an attempts
    if play["details"]["winningPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_attempts"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_wins"] += 1
    elif play["details"]["winningPlayerId"] in \
            game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_attempts"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_wins"] += 1
    else:
        print("Faceoff Lost By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["shootingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_goal(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    home_goalie_in = bool(int(play["situationCode"][0]))
    away_goalie_in = bool(int(play["situationCode"][3]))
    home_strength = int(play["situationCode"][1])
    away_strength = int(play["situationCode"][2])

    # home shorthanded
    if ((home_goalie_in and away_goalie_in) and home_strength < away_strength) \
        or ((not home_goalie_in) and home_strength <= away_strength):
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["short_handed_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["power_play_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    
    # away shorthanded
    elif ((home_goalie_in and away_goalie_in) and away_strength < home_strength) \
        or ((not away_goalie_in) and away_strength <= home_strength):
        if play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["short_handed_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
        elif play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["power_play_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
            
    # empty net goals
    elif (not home_goalie_in):
        if play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["empty_net_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
        else:
            pass
    elif (not away_goalie_in):
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["empty_net_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
        else:
            pass

    # 4-on-4
    elif (home_strength == 4 and away_strength == 4):
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["4-on-4_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["4-on-4_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
        else:
            print("Faceoff Lost By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    
    # 3-on-3
    elif (home_strength == 3 and away_strength == 3):
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["3-on-3_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["3-on-3_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
        else:
            print("Faceoff Lost By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # even strength
    else:
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["even_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["even_goals"] += 1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
        else:
            print("Faceoff Lost By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())


def parse_play_by_play_data(game_data : dict={}, game_stats : dict={}) -> dict:
    home_team = game_data["box_score"]["homeTeam"]["name"]["default"]
    away_team = game_data["box_score"]["awayTeam"]["name"]["default"]

    # loop through every play in the game
    # TODO eventually I might just use this for all data but for now I'm just
    # filling in a few extra gaps
    for play in game_data["play_by_play"]["plays"]:
        play_type = play["typeDescKey"]

        # penalties
        if play_type == "penalty":
            parse_play_by_play_penalties(home_team, away_team, play, game_stats)
                
        # hits
        if play_type == "hit":
            parse_play_by_play_hits(home_team, away_team, play, game_stats)
                
        # takeaways and giveaways
        if play_type == "takeaway" or \
            play_type == "giveaway":
            parse_play_by_play_takeaways_and_giveaways(home_team, away_team,
                play, game_stats)
                
        # blocked shots
        if play_type == "blocked-shot" or play_type ==  "missed-shot" or\
            play_type == "shot-on-goal": 
            parse_play_by_play_shots(home_team, away_team, play,
                game_stats)

        # Faceoffs
        if play["typeDescKey"] == "faceoff":
            parse_play_by_play_faceoffs(home_team, away_team, play, game_stats)

        # goals
        if play["typeDescKey"] == "goal":
            parse_play_by_play_goal(home_team, away_team, play, game_stats)
    return game_stats


def collect_game_stats(game : dict={}) -> dict:

    # Create the default data sets
    home_id = game["box_score"]["homeTeam"]["id"]
    home_team = game["box_score"]["homeTeam"]["name"]["default"]
    away_team = game["box_score"]["awayTeam"]["name"]["default"]
    # print(game["box_score"]["gameDate"], game["box_score"]["id"],
    #     "\t" + home_team, "\t" + away_team)
    
    # if the game hasn't been played then just fill out the minimum struct to be
    # able to gather past info for prediction engine to run
    if game["box_score"]["gameState"] in ["FUT", "PRE"] or \
        game["box_score"]["gameType"] not in [2, 3]:
        game_stats = {
            "home_team" : home_team,
            "away_team" : away_team,
            "game_type" : game["box_score"]["gameType"],
        }
        return game_stats
    
    # if the game is finished create a table of all required data
    try: 
        game_stats = {
            "home_team" : home_team,
            "away_team" : away_team,
            "result" : game["box_score"]["periodDescriptor"]["periodType"],
            "game_type" : game["box_score"]["gameType"],
            home_team : {
                "team_stats" : {
                    "first_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][0]["home"]),
                    "second_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][1]["home"]),
                    "third_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][2]["home"]),
                    "shots" : int(game["box_score"]["homeTeam"]["sog"]),
                    "power_play_goals" :
                        int(game["box_score"]["boxscore"]["teamGameStats"][2][
                            "homeValue"].split("/")[0]),
                    "power_play_chances" : 
                        int(game["box_score"]["boxscore"]["teamGameStats"][2][
                            "homeValue"].split("/")[1]),
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 0,
                    "penalty_minutes" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][4]["homeValue"]),
                    "penalties_drawn" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][4]["awayValue"]),
                    "hits" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][5]["homeValue"]),
                    "getting_hit" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][5]["awayValue"]),
                    "blocks" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][6]["homeValue"]),
                    "blocked_shots" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][6]["awayValue"]),
                },
                "player_stats" : {}
            },
            away_team : {
                "team_stats" : {
                    "first_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][0]["home"]),
                    "second_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][1]["home"]),
                    "third_period_goals" :
                        int(game["box_score"]["boxscore"]["linescore"]
                            ["byPeriod"][2]["home"]),
                    "shots" : int(game["box_score"]["homeTeam"]["sog"]),
                    "power_play_goals" :
                        int(game["box_score"]["boxscore"]["teamGameStats"][2][
                            "homeValue"].split("/")[0]),
                    "power_play_chances" : 
                        int(game["box_score"]["boxscore"]["teamGameStats"][2][
                            "homeValue"].split("/")[1]),
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 0,
                    "penalty_minutes" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][4]["homeValue"]),
                    "penalties_drawn" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][4]["awayValue"]),
                    "hits" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][5]["homeValue"]),
                    "getting_hit" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][5]["awayValue"]),
                    "blocks" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][6]["homeValue"]),
                    "blocked_shots" : int(game["box_score"]["boxscore"][
                        "teamGameStats"][6]["awayValue"]),
                },
                "player_stats" : {}
            },
        }
    except KeyError as e:
        print(game["box_score"]["gameState"])
        print(game["box_score"]["id"])
        raise e

    # create a flat list of players by id so we can reference stats from
    # the boxscore when looping through play-by-play
    list_of_players = \
        game["box_score"]["boxscore"]["playerByGameStats"]["awayTeam"] \
            ["forwards"] + \
        game["box_score"]["boxscore"]["playerByGameStats"]["awayTeam"] \
            ["defense"] + \
        game["box_score"]["boxscore"]["playerByGameStats"]["awayTeam"] \
            ["goalies"] + \
        game["box_score"]["boxscore"]["playerByGameStats"]["homeTeam"] \
            ["forwards"] + \
        game["box_score"]["boxscore"]["playerByGameStats"]["homeTeam"] \
            ["defense"] + \
        game["box_score"]["boxscore"]["playerByGameStats"]["homeTeam"] \
            ["goalies"]
    players_by_id = {}
    for player in list_of_players:
        players_by_id[player["playerId"]] = player

    # loop through all players and create default data sets for them then add
    # to the default "player_stats" of the main dictionary
    for player in game["play_by_play"]["rosterSpots"]:
        player_id = player["playerId"]
        if player["teamId"] == home_id:

            # game_stats->home/away_team->player_stats->player_name->stats_dict
            if player["positionCode"] == "G":
                game_stats[home_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[0]),
                    "even_shots" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[1]),
                    "power_play_saves" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[0]),
                    "power_play_shots" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[1]),
                    "short_handed_saves" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[0]),
                    "short_handed_shots" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[1]),
                    "pentaly_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
            else:
                game_stats[home_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : int(players_by_id[player_id]["plusMinus"]),
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
        else:
            if player["positionCode"] == "G":
                game_stats[away_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[0]),
                    "even_shots" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[1]),
                    "power_play_saves" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[0]),
                    "power_play_shots" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[1]),
                    "short_handed_saves" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[0]),
                    "short_handed_shots" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[1]),
                    "pentaly_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
            else:
                game_stats[away_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : int(players_by_id[player_id]["plusMinus"]),
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }

    # now we go through each play in the play-by-play data and get other stats
    game_stats = parse_play_by_play_data(game, game_stats)

    # now go through all the plays of the game and get the accumulated stats
    return game_stats


def parse_web_match_data(game_date : str="") -> list:
    game_ids = []
    game_data = []

    # get a list of all games for the date to get the ids
    game_list = \
        "https://api-web.nhle.com/v1/score/" + game_date
    game_list_web_data = requests.get(game_list)
    game_list_parsed_data = json.loads(game_list_web_data.content)
    for game in game_list_parsed_data["games"]:
        game_ids.append(game["id"])

    # now that we have the id list, we can get the play-by-play data
    raw_game_stats = []
    for id in game_ids:
        play_by_play_list = "https://api-web.nhle.com/v1/gamecenter/" + \
            str(id) + "/play-by-play"
        play_by_play_list_web_data = requests.get(play_by_play_list)
        play_by_play_list_parsed_data = json.loads(
            play_by_play_list_web_data.content)
        box_score_list = "https://api-web.nhle.com/v1/gamecenter/" + \
            str(id) + "/boxscore"
        box_score_list_web_data = requests.get(box_score_list)
        box_score_list_parsed_data = json.loads(
            box_score_list_web_data.content)
        raw_game_stats.append({
            "play_by_play" : play_by_play_list_parsed_data,
            "box_score" : box_score_list_parsed_data
        })
        
    # now we have all the games as play-by-play data. run through each game and
    # create a dict of all used data
    for game in raw_game_stats:
        game_stats = collect_game_stats(game)
        game_stats['date'] = game_date
        game_data.append({"date" : game_date, "game_stats" : game_stats})
    return game_data


def get_game_records() -> None:

    # first get the list of all seasons to get the start and end date
    seasons = "https://api.nhle.com/stats/rest/en/season"
    seasons_web_data = requests.get(seasons)
    seasons_parsed_data = json.loads(seasons_web_data.content)

    # now we have to use the seasons list to get the specific dates of interest
    for season in seasons_parsed_data["data"]:
        if season["id"] == SEASON:
            start_date = datetime.datetime.fromisoformat(
                    (season["startDate"] + ".00")[:-1]
                ).astimezone(datetime.timezone.utc).date()
            end_date = datetime.datetime.fromisoformat(
                    (season["regularSeasonEndDate"] + ".00")[:-1]
                ).astimezone(datetime.timezone.utc).date()
            break
    # TODO: we will have to find a way to update the end date to get the dates
    # for the post season too. If the season is over it has endDate, but if we
    # are parsing the currents season then it doesn't have that info

    # create a list of all dates between now and season end
    # dates = pandas.date_range(start_date, end_date).to_pydatetime().tolist()
    dates = [start_date]
    i = 0
    for date in dates:
        dates[i] = date.strftime("%Y-%m-%d")
        i += 1
    current_date = datetime.date.today()
    match_parser_process_list = []
    for i in range(15):
        match_parser_process_list.append(Process(target=worker_node,
            args=(match_input_queue, match_output_queue))
        )
    for process in match_parser_process_list:
        process.start()

    # matches are orginized by date they take place
    for date in dates:

        # for each game on a specific date loop through
        match_input_queue.put((parse_web_match_data, ([date])))
    for i in range(15):
        match_input_queue.put('STOP')
    for i in range(15):
        for output_list in iter(match_output_queue.get, 'STOP'):
            if (output_list is not None) and (len(output_list) > 0):
                parsed_date = output_list[0]['date'].split("-")
                parsed_date = datetime.date(int(parsed_date[0]),
                    int(parsed_date[1]), int(parsed_date[2]))

                # if the date has already passed, then do post processing
                if parsed_date < current_date:

                    # if regular season then put into that list of dates
                    if output_list[0]['game_stats']['game_type'] == 2:
                        regular_season_matches[output_list[0]['date']] = \
                            output_list

                    # otherwise put the date and all games into the playoff
                    # list of matches
                    else:
                        playoff_matches[output_list[0]['date']] = output_list

                # otherwise slate it for the prediction engine
                else:
                    upcoming_matches[output_list[0]['date']] = output_list
                    # if output_list[0]['linescore']['gameType'] == "R":
                    #     upcoming_matches[output_list[0]['date']] = output_list
                    # else:
                    #     upcoming_playoff_matches[output_list[0]['date']] = \
                    #         output_list

    # close all parser processes
    for process in match_parser_process_list:
        process.join()


def worker_node(input_queue : Queue=None, output_queue : Queue=None) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    output_queue.put('STOP')


def get_team_trend_by_date(home_team : str="", away_team : str="",
    ranking_date : str="") -> list:

    # if the game took place before any rankings were available just
    # give average scores to both teams for weighting
    if ranking_date == "":
        clutch_stats = [0.5, 0.5]
        defensive_stats = [0.5, 0.5]
        offensive_stats = [0.5, 0.5]
        recent_form_stats = [0.5, 0.5]
        sos_stats = [0.5, 0.5]
        total_rating_stats = [0.5, 0.5]

    # find the correct scale factors for each team
    else :

        # if the home team does not have a ranking because they have not
        # played yet then default them to 0.5, same for away
        if not (home_team in total_rating_trend[ranking_date]):
            clutch_rating_get_trend_dict()[
                ranking_date][home_team] = 0.5
            defensive_rating_get_trend_dict()[
                ranking_date][home_team] = 0.5
            offensive_rating_get_trend_dict()[
                ranking_date][home_team] = 0.5
            recent_form_get_trend_dict()[
                ranking_date][home_team] = 0.5
            strength_of_schedule_get_trend_dict()[
                ranking_date][home_team] = 0.5
            ranking_absolutes[ranking_date][home_team] = 0.5
            ranking_averages[ranking_date][home_team] = 0.5
            total_rating_trend[ranking_date][home_team] = 0.5
        if not (away_team in total_rating_trend[ranking_date]):
            clutch_rating_get_trend_dict()[
                ranking_date][away_team] = 0.5
            defensive_rating_get_trend_dict()[
                ranking_date][away_team] = 0.5
            offensive_rating_get_trend_dict()[
                ranking_date][away_team] = 0.5
            recent_form_get_trend_dict()[
                ranking_date][away_team] = 0.5
            strength_of_schedule_get_trend_dict()[
                ranking_date][away_team] = 0.5
            ranking_absolutes[ranking_date][away_team] = 0.5
            ranking_averages[ranking_date][away_team] = 0.5
            total_rating_trend[ranking_date][away_team] = 0.5

        # clutch trends don't really counter eachother so pass total
        # rating score to scale instead
        clutch_stats = [
            total_rating_trend[ranking_date][home_team],
            total_rating_trend[ranking_date][away_team]
        ]
        defensive_stats = [
            defensive_rating_get_trend_dict()[ranking_date][home_team],
            defensive_rating_get_trend_dict()[ranking_date][away_team]
        ]
        offensive_stats = [
            offensive_rating_get_trend_dict()[ranking_date][home_team],
            offensive_rating_get_trend_dict()[ranking_date][away_team]
        ]
        recent_form_stats = [
            recent_form_get_trend_dict()[ranking_date][home_team],
            recent_form_get_trend_dict()[ranking_date][away_team]
        ]
        sos_stats = [
            strength_of_schedule_get_trend_dict()[ranking_date][home_team],
            strength_of_schedule_get_trend_dict()[ranking_date][away_team]
        ]
        total_rating_stats = [
            total_rating_trend[ranking_date][home_team],
            total_rating_trend[ranking_date][away_team]
        ]
    return [clutch_stats, defensive_stats, offensive_stats, recent_form_stats,
        sos_stats, total_rating_stats]


def parse_team_match_data(match_data : dict={}, relative_metrics : list=[]) \
                                                                        -> list:
    metric_data = []

    # get home and away team
    away_team = match_data["game_stats"]["away_team"]
    home_team = match_data["game_stats"]["home_team"]

    ### clutch rating ###
    clutch_data = clutch_calculate_lead_protection(match_data)
    clutch_data[home_team] *= (
        1 + relative_metrics[Metric_Order.CLUTCH.value][
            Team_Selection.AWAY.value]
    )
    clutch_data[away_team] *= (
        1 + relative_metrics[Metric_Order.CLUTCH.value][
            Team_Selection.HOME.value]
    )
    metric_data.append(clutch_data)

    ### defensive rating ###
    # shots against
    defensive_data = defensive_rating_get_data_set(match_data)
    defensive_data['shots_against'][home_team] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    defensive_data['shots_against'][away_team] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    )

    # goals against
    defensive_data['goals_against'][home_team] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    defensive_data['goals_against'][away_team] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    )

    # penalty kill goals against
    defensive_data['penalty_kill_data'][home_team][0] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    defensive_data['penalty_kill_data'][away_team][0] /= (
        1 + relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    )
    metric_data.append(defensive_data)

    ### offensive rating ###
    # shots for
    offensive_data = offensive_rating_get_data_set(match_data)
    offensive_data['shots_for'][home_team] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    offensive_data['shots_for'][away_team] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]
    )

    # goals for
    offensive_data['goals_for'][home_team] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    offensive_data['goals_for'][away_team] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]
    )

    # power play goals for
    offensive_data['power_play_data'][home_team][0] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    )
    offensive_data['power_play_data'][away_team][0] *= (
        1 + relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]
    )
    metric_data.append(offensive_data)

    ### recent form ###
    recent_form_data = recent_form_get_data_set(match_data)
    recent_form_data[1][home_team] *= (
        1 + relative_metrics[Metric_Order.RECENT.value][
            Team_Selection.AWAY.value]
    )
    recent_form_data[1][away_team] *= (
        1 + relative_metrics[Metric_Order.RECENT.value][
            Team_Selection.HOME.value]
    )
    metric_data.append(recent_form_data)

    ### strength of schedule
    sos_data = strength_of_schedule_get_data_set(match_data)
    sos_data[home_team] *= (
        1 + relative_metrics[Metric_Order.SOS.value][Team_Selection.AWAY.value]
    )
    sos_data[away_team] *= (
        1 + relative_metrics[Metric_Order.SOS.value][Team_Selection.HOME.value]
    )
    metric_data.append(sos_data)

    # return the list of all metric data for this match
    return metric_data


def parse_player_match_data(match_data : dict={}, relative_metrics : list=[],
    player_list : list=[]) -> list:
    metric_data = []
    goalie_metrics = []
    forward_metrics = []
    defensemen_metrics = []
    goalies = player_list[0]
    forwards = player_list[1]
    defensemen = player_list[2]

    # get home and away team
    home_team = match_data["game_stats"]["home_team"]

    ### Goalie Stats ###
    goalie_utilization_data = utilization_get_data_set(goalies)
    goalie_goals_against_data = goalie_goals_against_get_data_set(goalies)
    goalie_save_per_data = goalie_save_percentage_get_data_set(goalies)
    goalie_save_consistency_data = goalie_save_consistency_get_data_set(goalies)

    # unlike team engine, run all relative scaling at the end of the section
    for goalie in goalies:

        # if the player is on the home team
        if goalies[goalie]['team'] == home_team:

            # Utilization
            goalie_utilization_data[goalie]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
            # Goals Against
            goalie_goals_against_data[goalie] *= \
                (1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Save Percentage
            goalie_save_per_data['even_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            goalie_save_per_data['pp_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            goalie_save_per_data['pk_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Save Consistency
            goalie_save_consistency_data[goalie] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
        else:

            # Utilization
            goalie_utilization_data[goalie]["time_on_ice"] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Goals Against
            goalie_goals_against_data[goalie] *= \
                (1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Save Percentage
            goalie_save_per_data['even_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            goalie_save_per_data['pp_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            goalie_save_per_data['pk_save_per'][goalie]['saves'] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Save Consistency
            goalie_save_consistency_data[goalie] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
    
    # Append Goalie metrics
    goalie_metrics.append(goalie_utilization_data)
    goalie_metrics.append(goalie_goals_against_data)
    goalie_metrics.append(goalie_save_per_data)
    goalie_metrics.append(goalie_save_consistency_data)

    ### Forward metrics
    forward_utilization_data = utilization_get_data_set(
        forwards)
    forward_blocks_data = blocks_get_data_set(forwards)
    forward_contributing_games_data = forward_contributing_games_get_data_set(
        forwards)
    forward_discipline_data = forward_discipline_get_data(forwards)
    forward_hits_data = forward_hits_get_data_set(forwards)
    forward_multipoint_game_data = forward_multipoint_games_get_data_set(
        forwards)
    forward_plus_minus_data = forward_plus_minus_get_data_set(
        forwards)
    forward_total_points_data = forward_points_get_data_set(forwards)
    forward_takeaway_data = forward_takeaways_get_data_set(forwards)
    for forward in forwards:
        
        # if the player is on the home team
        if forwards[forward][0] == home_team:
            
            # Blocks
            forward_blocks_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Contributing Games
            forward_contributing_games_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Discipline
            forward_discipline_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Hits
            forward_hits_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            
            # Multipoint Games
            forward_multipoint_game_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Plus Minus
            forward_plus_minus_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            
            # Total Points
            forward_total_points_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Takeaways
            forward_takeaway_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Utilization
            forward_utilization_data[1][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            forward_utilization_data[2][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            forward_utilization_data[3][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
        else:
            
            # Blocks
            forward_blocks_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Contributing Games
            forward_contributing_games_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Discipline
            forward_discipline_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Hits
            forward_hits_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Multipoint Games
            forward_multipoint_game_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Plus Minus
            forward_plus_minus_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Total Points
            forward_total_points_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Takeaways
            forward_takeaway_data[forward][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Utilization
            forward_utilization_data[1][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            forward_utilization_data[2][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            forward_utilization_data[3][forward] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
    
    # Append Forward Metrics
    forward_metrics.append(forward_utilization_data)
    forward_metrics.append(forward_blocks_data)
    forward_metrics.append(forward_discipline_data)
    forward_metrics.append(forward_hits_data)
    forward_metrics.append(forward_plus_minus_data)
    forward_metrics.append(forward_total_points_data)
    forward_metrics.append(forward_takeaway_data)
    forward_metrics.append(forward_contributing_games_data)
    forward_metrics.append(forward_multipoint_game_data)

    ### Defensemen Metrics
    defensemen_utilization_data = utilization_get_data_set(
        defensemen)
    defensemen_blocks_data = blocks_get_data_set(defensemen)
    defensemen_discipline_data = defensemen_discipline_get_data(defensemen)
    defensemen_hits_data = defensemen_hits_get_data_set(defensemen)
    defensemen_plus_minus_data = defensemen_plus_minus_get_data_set(
        defensemen)
    defensemen_points_data = defensemen_points_get_data_set(defensemen)
    defensemen_takeaway_data = defensemen_takeaways_get_data_set(defensemen)
    for defenseman in defensemen:
        
        # if the player is on the home team
        if defensemen[defenseman][0] == home_team:

            # Blocks
            defensemen_blocks_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Discipline
            defensemen_discipline_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Hits
            defensemen_hits_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            
            # Plus Minus
            defensemen_plus_minus_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            
            # Takeaways
            defensemen_takeaway_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Total Points
            defensemen_points_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Utilization
            defensemen_utilization_data[1][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            defensemen_utilization_data[2][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            defensemen_utilization_data[3][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
        else:

            # Blocks
            defensemen_blocks_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Discipline
            defensemen_discipline_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Hits
            defensemen_hits_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Plus Minus
            defensemen_plus_minus_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Takeaways
            defensemen_takeaway_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Total Points
            defensemen_points_data[defenseman][1] *= \
                (1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Utilization
            defensemen_utilization_data[1][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            defensemen_utilization_data[2][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            defensemen_utilization_data[3][defenseman] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
    
    # Append Defensemen Metrics
    defensemen_metrics.append(defensemen_utilization_data)
    defensemen_metrics.append(defensemen_blocks_data)
    defensemen_metrics.append(defensemen_discipline_data)
    defensemen_metrics.append(defensemen_hits_data)
    defensemen_metrics.append(defensemen_plus_minus_data)
    defensemen_metrics.append(defensemen_points_data)
    defensemen_metrics.append(defensemen_takeaway_data)

    # Append all player metrics
    metric_data.append(goalie_metrics)
    metric_data.append(forward_metrics)
    metric_data.append(defensemen_metrics)
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
                time_on_ice = \
                    float(players[player_by_ID]["time_on_ice"].split(":")[0]) +\
                    (float(players[player_by_ID]["time_on_ice"].split(":")[1]) 
                        / 60)
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
                time_on_ice = \
                    float(players[player_by_ID]["time_on_ice"].split(":")[0]) +\
                    (float(players[player_by_ID]["time_on_ice"].split(":")[1]) 
                        / 60)
                if time_on_ice > 0:
                    stats = players[player_by_ID]
                else:
                    stats = None

                # sort all the players in this match to parse their data
                if (position == 'G') and (stats != None):
                    print(name)
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
            

def plot_uncorrected_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    ### Clutch Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}ClutchRatingBase.csv".format(
            prefix
        ),
        ["Team", "Clutch Rating Base"], clutch_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}ClutchRatingBase.csv".format(
            prefix
        ),
        ["Team", "Clutch Rating Base"], 0.0, 0.0, [],
        "Graphs/Teams/Clutch_Rating/{}clutch_rating_base.png".format(prefix))))

    ### Defensive Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"],
        defensive_rating_get_shots_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/{}".format(prefix) +
            "shots_against_per_game_base.png",
        True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"],
        defensive_rating_get_goals_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/{}".format(prefix) +
            "goals_against_per_game_base.png",
        True)))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}PKRatingBase.csv".format(
            prefix),
        ["Team", "Penalty Kill Base"], defensive_rating_get_pk_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}PKRatingBase.csv".format(
            prefix
        ),
        ["Team", "Penalty Kill Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/{}penalty_kill_base.png".format(prefix))
    ))

    ### Offensive Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], offensive_rating_get_shots_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/{}shots_for_per_game_base.png".format(
            prefix))
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], offensive_rating_get_goals_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/{}goals_for_per_game_base.png".format(
            prefix))
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PPRatingBase.csv",
        ["Team", "Power Play Base"], offensive_rating_get_pp_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PPRatingBase.csv",
        ["Team", "Power Play Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/{}power_play_base.png".format(prefix))
    ))

    ### Recent Form ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], recent_form_get_streak_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], 0.0, 0.0, [],
        "Graphs/Teams/Recent_Form/{}recent_form_streak_base.png".format(prefix))
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_ten_base.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], 20.0, 0,
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_twenty_base.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], 40.0, 0,
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40],
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_fourty_base.png")
    ))

    ### Strength of Schedule
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], strength_of_schedule_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], 0.0, 0.0, [],
        "Graphs/Teams/Strength_of_Schedule/{}sos_base.png".format(prefix))
    ))


def plot_corrected_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    ### Clutch Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], clutch_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/{}clutch_rating_final.png".format(prefix))
    ))

    ### Defensive Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"],
        defensive_rating_get_shots_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/{}".format(prefix) +
            "shots_against_per_game_sigmoid.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"],
        defensive_rating_get_goals_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) + 
            "GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/{}".format(prefix) +
            "goals_against_per_game_sigmoid.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], defensive_rating_get_pk_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/{}".format(prefix) +
            "penalty_kill_sigmoid.png")
    ))

    ### Offensive Rating ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], offensive_rating_get_shots_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/{}".format(prefix) +
            "shots_for_per_game_sigmoid.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], offensive_rating_get_goals_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/{}".format(prefix) +
            "goals_for_per_game_sigmoid.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], offensive_rating_get_pp_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/{}power_play_sigmoid.png".format(prefix))
    ))

    ### Recent Form ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"],
        recent_form_get_streak_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_streak_corrected.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_ten_corrected.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_twenty_corrected.png")
    ))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}".format(prefix) +
            "recent_form_last_fourty_corrected.png")
    ))

    ### Strength of Schedule ###
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"],
        strength_of_schedule_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}".format(prefix) +
            "StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Strength_of_Schedule/{}".format(prefix) +
            "strenght_of_schedule_final.png")
    ))
    

def plot_combined_team_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}DefensiveRating.csv".format(
            prefix
        ),
        ["Team", "Defensive Rating Final"], defensive_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}DefensiveRating.csv".format(
            prefix
        ),
        ["Team", "Defensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/{}defensive_rating_final.png".format(
            prefix
        ))))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}OffensiveRating.csv".format(
            prefix
        ),
        ["Team", "Offensive Rating Final"], offensive_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}OffensiveRating.csv".format(
            prefix
        ),
        ["Team", "Offensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/{}offensive_rating_final.png".format(
            prefix
        ))))
    write_out_file(
        "Output_Files/Team_Files/Instance_Files/{}RecentFormFinal.csv".format(
            prefix
        ),
        ["Team", "Recent Form Rating"], recent_form_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/{}RecentFormFinal.csv".format(
            prefix
        ),
        ["Team", "Recent Form Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}recent_form_final.png".format(
            prefix
        ))))
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

    # clutch
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}ClutchRating.csv".format(
            prefix
        ),
        clutch_rating_get_trend_dict(), "Clutch Rating")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}ClutchRating.csv".format(
            prefix
        ),
        ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/{}clutch_rating_trend.png".format(
            prefix
        ))))

    # defensive rating
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}DefensiveRating.csv".format(
            prefix
        ),
        defensive_rating_get_trend_dict(), "Defensive Rating")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}DefensiveRating.csv".format(
            prefix
        ),
        ["Rating Date", "Defensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/{}defensive_rating_trend.png".format(
            prefix
        ))))
    
    # offensive rating
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}OffensiveRating.csv".format(
            prefix
        ),
        offensive_rating_get_trend_dict(), "Offensive Rating")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}OffensiveRating.csv".format(
            prefix
        ),
        ["Rating Date", "Offensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/{}offensive_rating_trend.png".format(
            prefix
        ))))
    
    # recent form
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}RecentForm.csv".format(
            prefix
        ),
        recent_form_get_trend_dict(), "Recent Form")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}RecentForm.csv".format(
            prefix
        ),
        ["Rating Date", "Recent Form"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/{}recent_form_trend.png".format(
            prefix
        ))))
    
    # strength of schedule
    update_trend_file(
        "Output_Files/Team_Files/Trend_Files/{}StrengthOfSchedule.csv".format(
            prefix
        ),
        strength_of_schedule_get_trend_dict(),
        "Strength of Schedule")
    plotting_queue.put((plot_team_trend_set,
        ("Output_Files/Team_Files/Trend_Files/{}StrengthOfSchedule.csv".format(
            prefix
        ),
        ["Rating Date", "Strength of Schedule"], 1.1, -.1, 
        sigmoid_ticks, "Graphs/Teams/Strength_of_Schedule/" + 
            "{}strength_of_schedule_trend.png".format(
            prefix
        ))))

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
        ["Goalie", "Utilization Base", "Team"], utilization_base_get_dict("G"),
        goalie_teams)
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
        goalie_goals_against_get_dict(), goalie_teams, False)
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
        goalie_save_percentage_get_dict(), goalie_teams)
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
        goalie_save_consistency_get_dict(), goalie_teams)
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
        ["Forward", "Blocks Base", "Team"], blocks_base_get_dict("C"),
        forward_teams)
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
        forward_contributing_games_get_dict(), forward_teams)
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
        forward_discipline_get_dict(), forward_teams, False)
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
        forward_hits_get_dict(), forward_teams, True)
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
        forward_multipoint_games_get_dict(), forward_teams, True)
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
        forward_plus_minus_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Forward/Plus_Minus/{}plus_minus_base.png".format(prefix),
        False)
    ))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}Takeaways_Base.csv".format(
            prefix
        ),
        ["Forward", "Takeaways Base", "Team"],
        forward_takeaways_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/{}Takeaways_Base.csv".format(
            prefix
        ),
        ["Forward", "Takeaways Base"], 0.0, 0.0, [],
        "Graphs/Forward/Takeaways/{}takeaways_base.png".format(prefix),
            False)
    ))
    
    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Base.csv",
        ["Forward", "Points Base", "Team"],
        forward_points_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Base.csv",
        ["Forward", "Points Base"], 0.0, 0.0, [],
        "Graphs/Forward/Total_Points/{}total_points_base.png".format(prefix),
        False)
    ))
    
    # Utilization
    # (Only generic TOI currently available, do not graph based on strength)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base", "Team"],
        utilization_base_get_dict("C"), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/{}even_utilzation_base.png".format(prefix),
        False)
    ))
    # write_out_player_file(
    #     "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
    #         "PPUtilization_Base.csv",
    #     ["Forward", "Power Play Utilization Base", "Team"],
    #     forward_utilization_get_pp_time_dict(), forward_teams, True)
    # plotting_queue.put((plot_player_ranking,
    #     ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
    #         "PPUtilization_Base.csv",
    #     ["Forward", "Power Play Utilization Base"], 0.0, 0.0, [],
    #     "Graphs/Forward/Utilization/{}pp_utilization_base.png".format(prefix),
    #     False)
    # ))
    # write_out_player_file(
    #     "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
    #         "PKUtilization_Base.csv",
    #     ["Forward", "Penalty Kill Utilization Base", "Team"],
    #     forward_utilization_get_pk_time_dict(), forward_teams, True)
    # plotting_queue.put((plot_player_ranking,
    #     ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
    #         "PKUtilization_Base.csv",
    #     ["Forward", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
    #     "Graphs/Forward/Utilization/{}pk_utilization_base.png".format(prefix),
    #     False)
    # ))
    
    ### Defensemen
    # Blocks
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}Blocks_Base.csv".format(
            prefix),
        ["Defensemen", "Blocks Base", "Team"],
        blocks_base_get_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Base.csv",
        ["Defensemen", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Blocks/{}blocks_base.png".format(prefix))
    ))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Defensemen", "Discipline Base", "Team"],
        defensemen_discipline_get_dict(), defensemen_teams, False)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Base.csv",
        ["Defensemen", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Discipline/{}discipline_base.png".format(prefix),
        True)
    ))
    
    # Utilization
    # (Only generic TOI currently available, do not graph based on strength)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base", "Team"],
        utilization_base_get_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, 
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/{}".format(prefix) +
            "even_utilzation_base.png",
        False)
    ))
    # write_out_player_file(
    #     "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
    #         "PPUtilization_Base.csv",
    #     ["Defensemen", "Power Play Utilization Base", "Team"],
    #     defensemen_utilization_get_pp_time_dict(), defensemen_teams, True)
    # plotting_queue.put((plot_player_ranking,
    #     ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
    #         "PPUtilization_Base.csv",
    #     ["Defensemen", "Power Play Utilization Base"], 0.0, 0.0, [],
    #     "Graphs/Defensemen/Utilization/{}pp_utilization_base.png".format(prefix),
    #     False)
    # ))
    # write_out_player_file(
    #     "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
    #         "PKUtilization_Base.csv",
    #     ["Defensemen", "Penalty Kill Utilization Base", "Team"],
    #     defensemen_utilization_get_pk_time_dict(), defensemen_teams, True)
    # plotting_queue.put((plot_player_ranking,
    #     ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
    #         "PKUtilization_Base.csv",
    #     ["Defensemen", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
    #     "Graphs/Defensemen/Utilization/{}pk_utilization_base.png".format(prefix),
    #     False)
    # ))
    
    # Hits
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix),
        ["Defensemen", "Hits Base", "Team"],
        defensemen_hits_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}Hits_Base.csv".format(
            prefix),
        ["Defensemen", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Hits/{}hits_base.png".format(prefix), False)
    ))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base", "Team"],
        defensemen_plus_minus_get_dict(), defensemen_teams, True)
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
        defensemen_points_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Base.csv",
        ["Defensemen", "Points Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Points/points_base.png".format(prefix),
        False)
    ))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Base.csv",
        ["Defensemen", "Takeaways Base", "Team"],
        defensemen_takeaways_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Base.csv",
        ["Defensemen", "Takeaways Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Takeaways/{}takeaways_base.png".format(prefix),
        False)
    ))


def plot_corrected_player_metrics(game_types : str="R") -> None:
    if game_types == "R":
        prefix = "Reg_Season_"
    else:
        prefix = "Post_Season_"

    ### Goalies
    # Utilization
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected", "Team"],
        utilization_rating_get_dict("G"), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Utilization/{}utilization_corrected.png".format(prefix))
    ))
    
    # Goals Against
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected", "Team"],
        goalie_goals_against_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goals_Against/{}goals_against_corrected.png".format(
            prefix))
    ))
    
    # Save Percentage
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected", "Team"],
        goalie_save_percentage_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Percentage/{}save_percentage_corrected.png".format(
            prefix))
        ))
    
    # Save Consistency
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected", "Team"],
        goalie_save_consistency_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Goalie_Files/Instance_Files/{}".format(prefix) +
            "Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Consistency/{}".format(prefix) +
            "save_consistency_corrected.png")
    ))
    
    ### Forwards
    # Blocks
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Forward", "Blocks Corrected", "Team"],
        blocks_rating_get_dict("C"), forward_teams)
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
        forward_contributing_games_get_dict(), forward_teams)
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
        forward_discipline_get_dict(), forward_teams)
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
        forward_hits_get_dict(), forward_teams)
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
        forward_multipoint_games_get_dict(), forward_teams, True)
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
        forward_plus_minus_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Plus_Minus/{}plus_minus_corrected.png".format(prefix))
    ))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Corrected.csv",
        ["Forward", "Takeaways Corrected", "Team"],
        forward_takeaways_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Corrected.csv",
        ["Forward", "Takeaways Corrected"], 0.0, 0.0, [],
        "Graphs/Forward/Takeaways/{}takeaways_corrected.png".format(prefix),
        False)
    ))
    
    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/{}".format(prefix) +
            "Total_Points_Corrected.csv",
        ["Forward", "Points Corrected", "Team"],
        forward_points_get_dict(), forward_teams)
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
        utilization_rating_get_dict("C"), forward_teams, True)
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
        blocks_rating_get_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Blocks/{}blocks_corrected.png".format(prefix))
    ))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected", "Team"],
        defensemen_discipline_get_dict(), defensemen_teams)
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
        defensemen_hits_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Hits/{}hits_corrected.png".format(prefix))))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected", "Team"],
        defensemen_plus_minus_get_dict(), defensemen_teams)
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
        defensemen_points_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Corrected.csv",
        ["Defensemen", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Points/{}points_corrected.png".format(prefix))
    ))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Corrected.csv",
        ["Defensemen", "Takeaways Corrected", "Team"],
        defensemen_takeaways_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Takeaways_Corrected.csv",
        ["Defensemen", "Takeaways Corrected"], 0.0, 0.0, [],
        "Graphs/Defensemen/Takeaways/{}takeaways_corrected.png".format(prefix))
    ))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "UtilizationRating.csv",
        ["Defensemen", "Utilization Rating", "Team"],
        utilization_rating_get_dict("D"), defensemen_teams)
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
    for team in clutch_rating_get_dict().keys():
        team_total_rating[team] = \
            (clutch_rating_get_dict()[team] *
                total_rating_weights.CLUTCH_RATING_WEIGHT.value) + \
            (defensive_rating_get_dict()[team] *
                total_rating_weights.DEFENSIVE_RATING_WEIGHT.value) + \
            (offensive_rating_get_dict()[team] *
                total_rating_weights.OFFENSIVE_RATING_WEIGHT.value) + \
            (recent_form_get_dict()[team] *
                total_rating_weights.RECENT_FORM_RATING_WEIGHT.value) + \
            (strength_of_schedule_get_dict()[team] *
                total_rating_weights.SOS_RATING_WEIGHT.value)
    

def run_played_game_parser_engine(game_types : str="R"):

    # loop through all gathered match dates until we have parsed all data
    if game_types == "R":
        sorted_date_list = sorted(regular_season_matches)
    elif game_types == "P":
        sorted_date_list = sorted(playoff_matches)
    else:

        # error input, return here
        return

    # determine at which dates we should collate and mark trend data
    i = 1
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

        # determine if this is the last date in the date list
        if ranking_period == all_ranking_periods[-1]:
            final_date = True

        # create a few match parsing processes to speed things up a bit
        subprocess_count = 15
        metric_process_list = []
        for i in range(subprocess_count):
            metric_process_list.append(Process(target=worker_node,
                args=(match_input_queue, match_output_queue))
            )
        for process in metric_process_list:
            process.start()

        # feed in matches until all those in the current date have been parsed
        if game_types == "R":
            run_match_parser(ranking_period, last_ranking_date,
                regular_season_matches)
        else:
            run_match_parser(ranking_period, last_ranking_date,
                playoff_matches)
    
        # let the metric workers know there are no more matches
        for i in range(subprocess_count):
            match_input_queue.put('STOP')
    
        # keep reading the metric output queue until all data is returned
        for i in range(subprocess_count):
            for output_list in iter(match_output_queue.get, 'STOP'):

                # check if we are getting a batch of player data or team data
                # players
                if len(output_list) == 3:

                    # Goalies
                    goalie_metrics = output_list[0]
                    goalie_utilization = goalie_metrics[0]  
                    utilization_add_match_data(goalie_utilization, "G")  
                    goalie_goals_against = goalie_metrics[1]
                    goalie_goals_against_add_match_data(goalie_goals_against)  
                    goalie_save_percentage = goalie_metrics[2]
                    goalie_save_percentage_add_match_data(
                        goalie_save_percentage)
                    goalie_save_consistency = goalie_metrics[3]
                    goalie_save_consistency_add_match_data(
                        goalie_save_consistency)
                    for goalie in goalie_utilization.keys():
                        goalie_teams[goalie] = \
                            goalie_utilization[goalie]['team']

                    # Forwards
                    forward_metrics = output_list[1]
                    forward_utilization = forward_metrics[0]
                    utilization_add_match_data(forward_utilization, "C")
                    forward_blocks = forward_metrics[1]
                    blocks_add_match_data(forward_blocks, "C")
                    forward_discipline = forward_metrics[2]
                    forward_discipline_add_match_data(forward_discipline)
                    forward_hits = forward_metrics[3]
                    forward_hits_add_match_data(forward_hits)
                    forward_plus_minus = forward_metrics[4]
                    forward_plus_minus_add_match_data(forward_plus_minus)
                    forward_points = forward_metrics[5]
                    forward_points_add_match_data(forward_points)
                    forward_takeaways = forward_metrics[6]
                    forward_takeaways_add_match_data(forward_takeaways)
                    forward_contribution = forward_metrics[7]
                    forward_contributing_games_add_match_data(
                        forward_contribution)
                    forward_multipoint = forward_metrics[8]
                    forward_multipoint_games_add_match_data(forward_multipoint)
                    for forward in forward_utilization[0].keys():
                        forward_teams[forward] = forward_utilization[0][forward]

                    # Defensemen
                    defensemen_metrics = output_list[2]
                    defensemen_utilization = defensemen_metrics[0]
                    utilization_add_match_data(defensemen_utilization, "D")
                    defensemen_blocks = defensemen_metrics[1]
                    blocks_add_match_data(defensemen_blocks, "D")
                    defensemen_discipline = defensemen_metrics[2]
                    defensemen_discipline_add_match_data(defensemen_discipline)
                    defensemen_hits = defensemen_metrics[3]
                    defensemen_hits_add_match_data(defensemen_hits)
                    defensemen_plus_minus = defensemen_metrics[4]
                    defensemen_plus_minus_add_match_data(defensemen_plus_minus)
                    defensemen_points = defensemen_metrics[5]
                    defensemen_points_add_match_data(defensemen_points)
                    defensemen_takeaways = defensemen_metrics[6]
                    defensemen_takeaways_add_match_data(defensemen_takeaways)
                    for defensemen in defensemen_utilization[0].keys():
                        defensemen_teams[defensemen] = \
                            defensemen_utilization[0][defensemen]
                        
                # teams
                else:

                    ### clutch data ###
                    clutch_return = output_list[Metric_Order.CLUTCH.value]
                    clutch_add_match_data(clutch_return)

                    ### defensive data ###
                    defensive_return = output_list[Metric_Order.DEFENSIVE.value]
                    defensive_rating_add_match_data(defensive_return)

                    ### offensive data ###
                    offensive_return = output_list[Metric_Order.OFFENSIVE.value]
                    offensive_rating_add_match_data(offensive_return)

                    ### recent form data ###
                    recent_form_return = output_list[Metric_Order.RECENT.value]
                    recent_form_add_match_data(recent_form_return)

                    ### strength of schedule data ###
                    sos_return = output_list[Metric_Order.SOS.value]
                    strength_of_schedule_add_match_data(sos_return)
        for process in metric_process_list:
            process.join()

##################### TEAM RANKING PERIOD PROCESSING ###########################
        # call any cleanup calculations required
        clutch_rating_scale_by_game()
        defensive_rating_calculate_all()
        offensive_rating_calculate_power_play()
        recent_form_calculate_all()
        strength_of_schedule_scale_by_game()

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
            # plot_uncorrected_team_metrics(game_types)

        # Clutch Rating
        apply_sigmoid_correction(clutch_rating_get_dict())

        # Defensive Rating
        apply_sigmoid_correction(defensive_rating_get_shots_against_dict(),
            True)
        apply_sigmoid_correction(defensive_rating_get_goals_against_dict(),
            True)
        apply_sigmoid_correction(defensive_rating_get_pk_dict())

        # Offensive Rating
        apply_sigmoid_correction(offensive_rating_get_shots_for_dict())
        apply_sigmoid_correction(offensive_rating_get_goals_for_dict())
        apply_sigmoid_correction(offensive_rating_get_pp_dict())

        # Recent Form
        apply_sigmoid_correction(recent_form_get_streak_dict())
        apply_sigmoid_correction(recent_form_get_last_10_dict())
        apply_sigmoid_correction(recent_form_get_last_20_dict())
        apply_sigmoid_correction(recent_form_get_last_40_dict())

        # Strenght of Schedule
        apply_sigmoid_correction(strength_of_schedule_get_dict())

        # write out any plots after sigmoid correction
        if final_date:
            print("Plot Team data after correction")
            # plot_corrected_team_metrics(game_types)

        ### plot multifactor metrics and total rating ###
        # Clutch rating
        # pass

        # Defensive Rating
        defensive_rating_combine_metrics()

        # Offensive Rating
        offensive_rating_combine_metrics()

        # Recent Form
        recent_form_combine_metrics()

        # combine all factors and plot the total rankings
        combine_all_team_factors()
        
        if final_date:
            pass
            # plot_combined_team_metrics(game_types)
            

        ### Update any trend sets if on ranking date ###
        # clutch
        clutch_update_trend(ranking_period[-1])
        
        # defensive rating
        defensive_rating_update_trends(ranking_period[-1])

        # offensive rating
        offensive_rating_update_trends(ranking_period[-1])

        # recent form
        recent_form_update_trends(ranking_period[-1])

        # strenght of schedule
        strength_of_schedule_update_trends(ranking_period[-1])

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
        utilization_scale_by_game(strength_of_schedule_get_games_played_dict(),
            goalie_teams, "G")
        apply_sigmoid_correction(utilization_base_get_dict("G"))

        goalie_goals_against_scale_by_utilization(
            utilization_rating_get_dict("G"))

        goalie_save_percentage_calculate_all()
        goalie_save_percentage_combine_metrics(
            strength_of_schedule_get_games_played_dict(),
            offensive_rating_get_pp_oppertunities_dict(),
            defensive_rating_get_pk_oppertunities_dict(),
            utilization_rating_get_dict("G"), goalie_teams)

        goalie_save_consistency_scale_by_games(
            strength_of_schedule_get_games_played_dict(), goalie_teams)

        ### Forwards ###
        utilization_scale_by_game(
            strength_of_schedule_get_games_played_dict(), forward_teams, "C")
        apply_sigmoid_correction(utilization_rating_get_dict("C"))

        blocks_scale_by_shots_against(
            defensive_rating_get_unscaled_shots_against_dict(), forward_teams,
            "C")

        forward_contributing_games_scale_by_games(
            strength_of_schedule_get_games_played_dict(), forward_teams)

        forward_discipline_scale_by_utilization(
            utilization_rating_get_dict("C"))

        forward_hits_scale_by_games(
            strength_of_schedule_get_games_played_dict(), forward_teams)

        forward_multipoint_games_scale_by_games(
            strength_of_schedule_get_games_played_dict(), forward_teams)

        forward_plus_minus_scale_by_utilization(
            utilization_rating_get_dict("C"))

        forward_points_scale_by_games(
            strength_of_schedule_get_games_played_dict(), forward_teams)

        forward_takeaways_scale_by_utilization(utilization_rating_get_dict("C"))

        ### Defensemen ###
        utilization_scale_by_game(
            strength_of_schedule_get_games_played_dict(), defensemen_teams, "D")
        apply_sigmoid_correction(utilization_base_get_dict("D"))

        blocks_scale_by_shots_against(
            defensive_rating_get_unscaled_shots_against_dict(),
            defensemen_teams, "D")

        defensemen_discipline_scale_by_utilization(
            utilization_rating_get_dict("D"))

        defensemen_hits_scale_by_games(
            strength_of_schedule_get_games_played_dict(), defensemen_teams)

        defensemen_plus_minus_scale_by_utilization(
            utilization_rating_get_dict("D"))

        defensemen_points_scale_by_games(
            strength_of_schedule_get_games_played_dict(), defensemen_teams)

        defensemen_takeaways_scale_by_utilization(
            utilization_rating_get_dict("D"))
        if final_date:
            print("Plot Player data before correction")
            plot_uncorrected_player_metrics(game_types)

        # Goalies
        apply_sigmoid_correction(goalie_goals_against_get_dict(), True)
        apply_sigmoid_correction(goalie_save_percentage_get_dict())
        apply_sigmoid_correction(goalie_save_consistency_get_dict())

        # Forwards
        apply_sigmoid_correction(blocks_rating_get_dict("C"))
        apply_sigmoid_correction(forward_discipline_get_dict(), True)
        apply_sigmoid_correction(forward_hits_get_dict())
        apply_sigmoid_correction(forward_plus_minus_get_dict())
        apply_sigmoid_correction(forward_points_get_dict())
        apply_sigmoid_correction(forward_takeaways_get_dict())
        apply_sigmoid_correction(forward_contributing_games_get_dict())
        apply_sigmoid_correction(forward_multipoint_games_get_dict())

        # Defensemen
        apply_sigmoid_correction(blocks_rating_get_dict("D"))
        apply_sigmoid_correction(defensemen_discipline_get_dict(), True)
        apply_sigmoid_correction(defensemen_hits_get_dict())
        apply_sigmoid_correction(defensemen_plus_minus_get_dict())
        apply_sigmoid_correction(defensemen_points_get_dict())
        apply_sigmoid_correction(defensemen_takeaways_get_dict())

        if final_date:
            print("Plot Player data after correction")
            # plot_corrected_player_metrics(game_types)

        ### combine metrics to overall score and plot ###
        # Goalies
        for goalie in utilization_rating_get_dict("G").keys():
            goalie_total_rating[goalie] = (
                (utilization_rating_get_dict("G")[goalie] *
                    goalie_rating_weights.UTILIZATION_WEIGHT.value) +
                (goalie_save_percentage_get_dict()[goalie] *
                    goalie_rating_weights.SAVE_PERCENTAGE_WEIGHT.value) +
                (goalie_goals_against_get_dict()[goalie] *
                    goalie_rating_weights.GOALS_AGAINST_WEIGHT.value) +
                (goalie_save_consistency_get_dict()[goalie] *
                    goalie_rating_weights.SAVE_CONSISTENCY_WEIGHT.value)
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
        for forward in utilization_rating_get_dict("C").keys():
            forward_total_rating[forward] = (
                (forward_hits_get_dict()[forward] *
                    forward_rating_weights.HITS_WEIGHT.value) +
                (blocks_rating_get_dict("C")[forward] *
                    forward_rating_weights.SHOT_BLOCKING_WEIGHT.value) +
                (utilization_rating_get_dict("C")[forward] *
                    forward_rating_weights.UTILIZATION_WEIGHT.value) +
                (forward_discipline_get_dict()[forward] *
                    forward_rating_weights.DISIPLINE_WEIGHT.value) +
                (forward_plus_minus_get_dict()[forward] *
                    forward_rating_weights.PLUS_MINUS_WEIGHT.value) +
                (forward_points_get_dict()[forward] *
                    forward_rating_weights.POINTS_WEIGHT.value) +
                (forward_takeaways_get_dict()[forward] *
                    forward_rating_weights.TAKEAWAYS_WEIGHT.value) +
                (forward_contributing_games_get_dict()[forward] *
                    forward_rating_weights.CONTRIBUTION_WEIGHT.value) +
                (forward_multipoint_games_get_dict()[forward] *
                    forward_rating_weights.MULTIPOINT_WEIGHT.value)
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
        for defensemen in utilization_rating_get_dict("D").keys():
            defensemen_total_rating[defensemen] = (
                (defensemen_hits_get_dict()[defensemen] *
                    defensemen_rating_weights.HITS_WEIGHT.value) +
                (blocks_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.SHOT_BLOCKING_WEIGHT.value) +
                (utilization_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.UTILIZATION_WEIGHT.value) +
                (defensemen_discipline_get_dict()[defensemen] *
                    defensemen_rating_weights.DISIPLINE_WEIGHT.value) +
                (defensemen_plus_minus_get_dict()[defensemen] *
                    defensemen_rating_weights.PLUS_MINUS_WEIGHT.value) +
                (defensemen_points_get_dict()[defensemen] *
                    defensemen_rating_weights.POINTS_WEIGHT.value) +
                (defensemen_takeaways_get_dict()[defensemen] *
                    defensemen_rating_weights.TAKEAWAYS_WEIGHT.value)
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
            pass
            plot_combined_player_metrics(game_types)

        # now update the last ranking date to indicate we have new trends
        last_ranking_date = ranking_period[-1]

############################# END POST PROCESSING ##############################
        # Print out trend files
        if final_date:

            ############## TEAMS ##############
            # plot_trend_team_metrics(game_types)
            
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
            # plot_average_player_team_metrics(game_types)

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
                writeout = [SEASON[0:4] + "-" + SEASON[4:]]
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
                writeout = [SEASON[0:4] + "-" + SEASON[4:]]
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
                writeout = [SEASON[0:4] + "-" + SEASON[4:]]
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
                writeout = [SEASON[0:4] + "-" + SEASON[4:]]
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
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Team_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Team_Files\Instance_Files\\" + file)
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Goalie_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Goalie_Files\Instance_Files\\" + file)
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Forward_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Forward_Files\Instance_Files\\" + file)
    for dir in \
        os.walk(os.getcwd() +
            "\Output_Files\Defensemen_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Defensemen_Files\Instance_Files\\" + file)
            

def calculate_metric_share(home_rating, away_rating) -> list:
    rating_total = home_rating + away_rating
    try:
        return [home_rating / rating_total, away_rating / rating_total]
    except ZeroDivisionError:
        return [0.5, 0.5]


def calculate_series_predictions(total_home_rating : float=0.0,
    total_away_rating : float=0.0, home_team : str="", away_team : str="") \
                                                                        -> None:

    # for any series which is not a 4-0, we must subtract the cases where
    # the losing team would win the last game, as those possbilities could never
    # actually happen. i.e we are not playing 7 random games and calculating the
    # odds of winning 4 which would be the basic (n choose k) we are instead
    # doing a special case were the 4th win by either team ends the set

    # first calculate the 4-0 odds for either team
    print("Base Odds:\n\t{} - {}\n\t{} - {}".format(
        home_team, total_home_rating, away_team, total_away_rating))
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


def run_upcoming_game_parser_engine() -> None:

    # loop through all gathered match dates until we have parsed all data
    final_team_ratings = {}
    sorted_date_list = sorted(upcoming_matches)

    # For now only parse the next 7 days of games because its too much damn data
    parsed_dates = 0
    for date in sorted_date_list:
        for match in upcoming_matches[date]:
            home_team = match["linescore"]["teams"]["home"]["team"]["name"]
            away_team = match["linescore"]["teams"]["away"]["team"]["name"]
            match_key = "{}: {} vs. {}".format(date, home_team, away_team)

            # some error catching for missing stats
            # Clutch Rating
            if home_team not in clutch_rating_get_dict().keys():
                home_stat = 0
            else:
                home_stat = clutch_rating_get_dict()[home_team]
            if away_team not in clutch_rating_get_dict().keys():
                away_stat = 0
            else:
                away_stat = clutch_rating_get_dict()[away_team]
            clutch_ratings = calculate_metric_share(home_stat, away_stat)

            # Defensive Ratings
            if home_team not in defensive_rating_get_dict().keys():
                home_stat = 0
            else:
                home_stat = defensive_rating_get_dict()[home_team]
            if away_team not in defensive_rating_get_dict().keys():
                away_stat = 0
            else:
                away_stat = defensive_rating_get_dict()[away_team]
            defensive_ratings = calculate_metric_share(home_stat, away_stat)

            # Offensive Ratings
            if home_team not in offensive_rating_get_dict().keys():
                home_stat = 0
            else:
                home_stat = offensive_rating_get_dict()[home_team]
            if away_team not in offensive_rating_get_dict().keys():
                away_stat = 0
            else:
                away_stat = offensive_rating_get_dict()[away_team]
            offensive_ratings = calculate_metric_share(home_stat, away_stat)

            # Recent Form
            if home_team not in recent_form_get_dict().keys():
                home_stat = 0
            else:
                home_stat = recent_form_get_dict()[home_team]
            if away_team not in recent_form_get_dict().keys():
                away_stat = 0
            else:
                away_stat = recent_form_get_dict()[away_team]
            recent_form_ratings = calculate_metric_share(home_stat, away_stat)

            # Strength of Schedule
            if home_team not in strength_of_schedule_get_dict().keys():
                home_stat = 0
            else:
                home_stat = strength_of_schedule_get_dict()[home_team]
            if away_team not in strength_of_schedule_get_dict().keys():
                away_stat = 0
            else:
                away_stat = strength_of_schedule_get_dict()[away_team]
            strength_of_schedule_ratings = calculate_metric_share(home_stat,
                away_stat)
            
            # Player rankings will exist if team has played at all no need for
            # extra checking here (I hope)
            goalie_average_ratings = calculate_metric_share(
                average_goalie_rating[home_team],
                average_goalie_rating[away_team])
            forward_average_ratings = calculate_metric_share(
                average_forward_rating[home_team],
                average_forward_rating[away_team])
            defenseman_average_ratings = calculate_metric_share(
                average_defenseman_rating[home_team],
                average_defenseman_rating[away_team])
            
            # Combine all ratings into final set
            final_team_ratings[match_key] = [(
                ((
                    (clutch_ratings[0] *
                        total_rating_weights.CLUTCH_RATING_WEIGHT.value) +
                    (defensive_ratings[0] *
                        total_rating_weights.DEFENSIVE_RATING_WEIGHT.value) +
                    (offensive_ratings[0] *
                        total_rating_weights.OFFENSIVE_RATING_WEIGHT.value) +
                    (recent_form_ratings[0] *
                        total_rating_weights.RECENT_FORM_RATING_WEIGHT.value) +
                    (strength_of_schedule_ratings[0] *
                        total_rating_weights.SOS_RATING_WEIGHT.value)
                ) * 0.70) +
                ((
                    (goalie_average_ratings[1] * 0.30) +
                    (forward_average_ratings[1] * 0.30) +
                    (defenseman_average_ratings[1] * 0.40)
                ) * 0.30)
            ),
            (
                ((
                    (clutch_ratings[1] *
                        total_rating_weights.CLUTCH_RATING_WEIGHT.value) +
                    (defensive_ratings[1] *
                        total_rating_weights.DEFENSIVE_RATING_WEIGHT.value) +
                    (offensive_ratings[1] *
                        total_rating_weights.OFFENSIVE_RATING_WEIGHT.value) +
                    (recent_form_ratings[1] *
                        total_rating_weights.RECENT_FORM_RATING_WEIGHT.value) +
                    (strength_of_schedule_ratings[1] *
                        total_rating_weights.SOS_RATING_WEIGHT.value)
                ) * 0.70) +
                ((
                    (goalie_average_ratings[0] * 0.30) +
                    (forward_average_ratings[0] * 0.30) +
                    (defenseman_average_ratings[0] * 0.40)
                ) * 0.30)
            ),
                clutch_ratings[0], clutch_ratings[1],
                defensive_ratings[0], defensive_ratings[1],
                offensive_ratings[0], offensive_ratings[1],
                recent_form_ratings[0], recent_form_ratings[1],
                strength_of_schedule_ratings[0],
                    strength_of_schedule_ratings[1],
                goalie_average_ratings[1], goalie_average_ratings[0],
                forward_average_ratings[1], forward_average_ratings[0],
                defenseman_average_ratings[1], defenseman_average_ratings[0],
            ]

        # Increment the number of parsed dates
        parsed_dates += 1
        if parsed_dates >= 7:
            break

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
            calculate_series_predictions(final_team_ratings[match][0],
                final_team_ratings[match][1], team_names[0], team_names[1])
            write_out_matches_file(
                "Output_Files/Team_Files/Trend_Files/{}.csv".format(file_name),
                ["Rating", "Home Odds", "Away Odds"],
                ["Total", "Clutch", "Defense", "Offense", "Recent Form",
                    "Strenght of Schedule", "Goalie Rating", "Forward Rating",
                    "Defenseman Rating"],
                final_team_ratings[match])
            plot_matches_ranking(
                "Output_Files/Team_Files/Trend_Files/{}.csv".format(file_name),
                [team_names[0], team_names[1]], sigmoid_ticks,
                "Graphs/Teams/Matches/{}.png".format(file_name))


if __name__ == "__main__":

    REG_SEASON_COMPLETE = False
    SEASON = 20232024
    TREND_FREQUENCY = 0
    TREND_DAY = 5
    start = time.time()
    freeze_support()

    parse_eye_test_file("player_eye_test.csv")
    
    # get all the match data
    match_data_start = time.time()
    print("Gathering All Match Data")
    get_game_records()
    print_time_diff(match_data_start, time.time())

    # automatically determine if the season is over based on the number of
    # unplayed matched found
    if len(upcoming_matches) == 0:
        print("Season Complete, Adding End Year Rankings\n")
        REG_SEASON_COMPLETE = True

    # if regular season games have been played then run post processing on those
    if len(regular_season_matches) > 0:
        print("Running Regular Season Post Process\n")
        run_played_game_parser_engine("R")

    exit(0)

    # reset all stats to just isolate post season.
    clutch_rating_reset()
    defensive_rating_reset()
    offensive_rating_reset()
    recent_form_reset()
    strength_of_schedule_reset()

    blocks_reset()
    utilization_reset()

    defensemen_discipline_reset()
    defensemen_hits_reset()
    defensmen_plus_minus_reset()
    defensemen_points_reset()
    defensemen_takeaways_reset()

    forward_contributing_games_reset()
    forward_discipline_reset()
    forward_hits_reset()
    forward_multipoint_games_reset()
    forward_plus_minus_reset()
    forward_takeaways_reset()
    forward_points_reset()

    goalie_goals_against_reset()
    goalie_save_consistency_reset()
    goalie_save_percentage_reset()

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
        print("Running Post Season Post Process\n")
        run_played_game_parser_engine("P")

    # if there are matches in the schedule that are still upcoming then process
    print_time_diff(start, time.time())
    start = time.time()

    if len(upcoming_matches) > 0:
        print("Running Post Season Match Predicter")
        run_upcoming_game_parser_engine()
    print_time_diff(start, time.time())
    exit(0)
