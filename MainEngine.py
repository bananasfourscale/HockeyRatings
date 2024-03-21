from multiprocessing import Process, Queue, freeze_support
import time
import os
import csv
import datetime
from enum import Enum

from Database_Parser import get_game_records

# import all custom team modules for statistical analysis
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_rating_get_trend_dict, clutch_rating_reset, \
    clutch_get_lead_data, clutch_add_match_data, \
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
from Shared_Metrics.Contributing_Games import contributing_games_base_get_dict,\
    contributing_games_rating_get_dict, contributing_games_reset, \
    contributing_games_get_data_set, contributing_games_add_match_data, \
    contributing_games_scale_by_games
from Shared_Metrics.Discipline import discipline_base_get_dict, \
    discipline_rating_get_dict, discipline_reset, discipline_get_data_set, \
    discipline_add_match_data, discipline_scale_by_utilization
from Shared_Metrics.Hitting import hitting_base_get_dict, \
    hitting_rating_get_dict, hitting_reset, hitting_get_data_set, \
    hitting_add_match_data, hitting_scale_by_game
from Shared_Metrics.Muiltipoint_Games import multipoint_base_get_dict, \
    multipoint_rating_get_dict, multipoint_reset, multipoint_get_data_set, \
    multipoint_add_match_data, multipoint_scale_by_game
from Shared_Metrics.PlusMinus import plus_minus_base_get_dict, \
    plus_minus_rating_get_dict, plus_minus_reset, plus_minus_get_data_set, \
    plus_minus_add_match_data, plus_minus_scale_by_utilization
from Shared_Metrics.Total_Points import total_points_base_get_dict, \
    total_points_rating_get_dict, total_points_reset, total_points_get_data_set, \
    total_points_add_match_data, total_points_scale_by_game
from Shared_Metrics.Turnovers import turnovers_base_get_dict, \
    turnovers_rating_get_dict, turnovers_reset, turnovers_get_data_set, \
    turnovers_add_match_data, turnovers_scale_by_utilization

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
    metric_data = {"team_data" : {}}

    # get home and away team
    away_team = match_data["game_stats"]["away_team"]
    home_team = match_data["game_stats"]["home_team"]

    ### clutch rating ###
    clutch_data = clutch_get_lead_data(match_data)
    clutch_data[home_team] *= (
        1 + relative_metrics[Metric_Order.CLUTCH.value][
            Team_Selection.AWAY.value]
    )
    clutch_data[away_team] *= (
        1 + relative_metrics[Metric_Order.CLUTCH.value][
            Team_Selection.HOME.value]
    )
    metric_data['team_data']['clutch_data'] = clutch_data

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
    metric_data['team_data']['defensive_data'] = defensive_data

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
    metric_data['team_data']['offensive_data'] = offensive_data

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
    metric_data['team_data']['recent_form_data'] = recent_form_data

    ### strength of schedule
    sos_data = strength_of_schedule_get_data_set(match_data)
    sos_data[home_team] *= (
        1 + relative_metrics[Metric_Order.SOS.value][Team_Selection.AWAY.value]
    )
    sos_data[away_team] *= (
        1 + relative_metrics[Metric_Order.SOS.value][Team_Selection.HOME.value]
    )
    metric_data['team_data']['sos_data'] = sos_data

    # return the list of all metric data for this match
    return metric_data


def parse_player_match_data(match_data : dict={}, relative_metrics : list=[],
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

    ### Goalie Stats ###
    goalie_utilization_data = utilization_get_data_set(goalies)
    goalie_discipline_data = discipline_get_data_set(goalies)
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

            # Discipline
            goalie_discipline_data[goalie]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )

            # Goals Against
            goalie_goals_against_data[goalie] *= (
                1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )

            # Save Percentage
            goalie_save_per_data['even_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            goalie_save_per_data['pp_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            goalie_save_per_data['pk_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )

            # Save Consistency
            goalie_save_consistency_data[goalie] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
        else:

            # Utilization
            goalie_utilization_data[goalie]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )

            # Discipline
            goalie_discipline_data[goalie]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Goals Against
            goalie_goals_against_data[goalie] *= (
                1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Save Percentage
            goalie_save_per_data['even_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            goalie_save_per_data['pp_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            goalie_save_per_data['pk_save_per'][goalie]['saves'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Save Consistency
            goalie_save_consistency_data[goalie] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
    
    # Append Goalie metrics
    goalie_metrics['utilization'] = goalie_utilization_data
    goalie_metrics['discipline'] = goalie_discipline_data
    goalie_metrics['goals_against'] = goalie_goals_against_data
    goalie_metrics['save_percentage'] = goalie_save_per_data
    goalie_metrics['save_consistency'] = goalie_save_consistency_data

    ### Forward metrics
    forward_utilization_data = utilization_get_data_set(
        forwards)
    forward_blocks_data = blocks_get_data_set(forwards)
    forward_contributing_games_data = contributing_games_get_data_set(
        forwards)
    forward_discipline_data = discipline_get_data_set(forwards)
    forward_hits_data = hitting_get_data_set(forwards)
    forward_multipoint_game_data = multipoint_get_data_set(forwards)
    forward_plus_minus_data = plus_minus_get_data_set(forwards)
    forward_points_data = total_points_get_data_set(forwards)
    forward_takeaway_data = turnovers_get_data_set(forwards)
    for forward in forwards:
        
        # if the player is on the home team
        if forward_utilization_data[forward]['team'] == home_team:
            
            # Blocks
            forward_blocks_data[forward]['blocks'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Contributing Games
            forward_contributing_games_data[forward]['contributing_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Discipline
            forward_discipline_data[forward]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Hits
            forward_hits_data[forward]['hitting'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
            # Multipoint Games
            forward_multipoint_game_data[forward]['multipoint_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Plus Minus
            forward_plus_minus_data[forward]['plus_minus'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
            # Total Points
            forward_points_data[forward]['total_points'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Turnovers
            forward_takeaway_data[forward]['turnovers'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Utilization
            forward_utilization_data[forward]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
        # if the player is on the away_team
        else:
            
            # Blocks
            forward_blocks_data[forward]['blocks'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Contributing Games
            forward_contributing_games_data[forward]['contributing_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Discipline
            forward_discipline_data[forward]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Hits
            forward_hits_data[forward]['hitting'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
            
            # Multipoint Games
            forward_multipoint_game_data[forward]['multipoint_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Plus Minus
            forward_plus_minus_data[forward]['plus_minus'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
            
            # Total Points
            forward_points_data[forward]['total_points'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Turnovers
            forward_takeaway_data[forward]['turnovers'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Utilization
            forward_utilization_data[forward]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
    
    # Append Forward Metrics
    forward_metrics['utilization'] = forward_utilization_data
    forward_metrics['blocks'] = forward_blocks_data
    forward_metrics['contributing_games'] = forward_contributing_games_data
    forward_metrics['discipline'] = forward_discipline_data
    forward_metrics['hits'] = forward_hits_data
    forward_metrics['multipoint_games'] = forward_multipoint_game_data
    forward_metrics['plus_minus'] = forward_plus_minus_data
    forward_metrics['total_points'] = forward_points_data
    forward_metrics['turnovers'] = forward_takeaway_data

    ### Defensemen Metrics
    defensemen_utilization_data = utilization_get_data_set(
        defensemen)
    defensemen_blocks_data = blocks_get_data_set(defensemen)
    defensemen_contributing_games_data = \
        contributing_games_get_data_set(defensemen)
    defensemen_discipline_data = discipline_get_data_set(defensemen)
    defensemen_hits_data = hitting_get_data_set(defensemen)
    defensemen_muiltipoint_data = multipoint_get_data_set(defensemen)
    defensemen_plus_minus_data = plus_minus_get_data_set(defensemen)
    defensemen_points_data = total_points_get_data_set(defensemen)
    defensemen_takeaway_data = turnovers_get_data_set(defensemen)
    for defenseman in defensemen:
        
        # if the player is on the home team
        if defensemen_utilization_data[defenseman]['team'] == home_team:

            # Blocks
            defensemen_blocks_data[defenseman]['blocks'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Contributing Games
            defensemen_contributing_games_data[defenseman][
                'contributing_games'] *= (
                    1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Discipline
            defensemen_discipline_data[defenseman]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Hits
            defensemen_hits_data[defenseman]['hitting'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
            # Muiltipoint Games
            defensemen_muiltipoint_data[defenseman]['multipoint_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Plus Minus
            defensemen_plus_minus_data[defenseman]['plus_minus'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
            
            # Turnovers
            defensemen_takeaway_data[defenseman]['turnovers'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Total Points
            defensemen_points_data[defenseman]['total_points'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.AWAY.value]
            )
            
            # Utilization
            defensemen_utilization_data[defenseman]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value]
            )
        else:

            # Blocks
            defensemen_blocks_data[defenseman]['blocks'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Contributing Games
            defensemen_contributing_games_data[defenseman][
                'contributing_games'] *= (
                    1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Discipline
            defensemen_discipline_data[defenseman]['penalty_net_minutes'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Hits
            defensemen_hits_data[defenseman]['hitting'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
            
            # Muiltipoint Games
            defensemen_muiltipoint_data[defenseman]['multipoint_games'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Plus Minus
            defensemen_plus_minus_data[defenseman]['plus_minus'] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
            
            # Turnovers
            defensemen_takeaway_data[defenseman]['turnovers'] *= (
                1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Total Points
            defensemen_points_data[defenseman]['total_points'] *= (
                1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                    Team_Selection.HOME.value]
            )
            
            # Utilization
            defensemen_utilization_data[defenseman]["time_on_ice"] *= (
                1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value]
            )
    
    # Append Defensemen Metrics
    defensemen_metrics['utilization'] = defensemen_utilization_data
    defensemen_metrics['blocks'] = defensemen_blocks_data
    defensemen_metrics['contributing_games'] = \
        defensemen_contributing_games_data
    defensemen_metrics['discipline'] = defensemen_discipline_data
    defensemen_metrics['hits'] = defensemen_hits_data
    defensemen_metrics['multipoint_games'] = defensemen_muiltipoint_data
    defensemen_metrics['plus_minus'] = defensemen_plus_minus_data
    defensemen_metrics['total_points'] = defensemen_points_data
    defensemen_metrics['turnovers'] = defensemen_takeaway_data

    # Append all player metrics
    metric_data['player_data']['goalie_metrics'] = goalie_metrics
    metric_data['player_data']['forward_metrics'] = forward_metrics
    metric_data['player_data']['defensemen_metrics'] = defensemen_metrics
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
        contributing_games_base_get_dict("C"), forward_teams)
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
        discipline_base_get_dict("C"), forward_teams, False)
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
        hitting_base_get_dict("C"), forward_teams, True)
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
        multipoint_base_get_dict("C"), forward_teams, True)
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
        plus_minus_base_get_dict("C"), forward_teams, True)
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
        turnovers_base_get_dict("C"), forward_teams, True)
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
        total_points_base_get_dict("C"), forward_teams, True)
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
        utilization_base_get_dict("C"), forward_teams, True)
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
        blocks_base_get_dict("D"), defensemen_teams)
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
        contributing_games_base_get_dict("D"), defensemen_teams)
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
        discipline_base_get_dict("D"), defensemen_teams, False)
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
        utilization_base_get_dict("D"), defensemen_teams, True)
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
        hitting_base_get_dict("D"), defensemen_teams, True)
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
        multipoint_base_get_dict("D"), defensemen_teams, True)
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
        plus_minus_base_get_dict("D"), defensemen_teams, True)
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
        total_points_base_get_dict("D"), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Base.csv",
        ["Defensemen", "Points Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Points/points_base.png".format(prefix),
        False)
    ))
    
    # Turnovers
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Base.csv",
        ["Defensemen", "Turnovers Base", "Team"],
        turnovers_base_get_dict("D"), defensemen_teams, True)
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
        contributing_games_rating_get_dict("C"), forward_teams)
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
        discipline_rating_get_dict("C"), forward_teams)
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
        hitting_rating_get_dict("C"), forward_teams)
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
        multipoint_rating_get_dict("C"), forward_teams, True)
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
        plus_minus_rating_get_dict("C"), forward_teams)
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
        turnovers_rating_get_dict("C"), forward_teams, True)
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
        total_points_rating_get_dict("C"), forward_teams)
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

    # Contributing Games
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Contribution_Corrected.csv",
        ["Defensemen", "Contribution Corrected", "Team"],
        contributing_games_rating_get_dict("D"), defensemen_teams)
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
        discipline_rating_get_dict("D"), defensemen_teams)
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
        hitting_rating_get_dict("D"), defensemen_teams)
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
        multipoint_rating_get_dict("D"), defensemen_teams, True)
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
        plus_minus_rating_get_dict("D"), defensemen_teams)
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
        total_points_rating_get_dict("D"), defensemen_teams)
    plotting_queue.put((plot_player_ranking,
        ("Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Points_Corrected.csv",
        ["Defensemen", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Points/{}points_corrected.png".format(prefix))
    ))
    
    # Turnovers
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/{}".format(prefix) +
            "Turnovers_Corrected.csv",
        ["Defensemen", "Turnovers Corrected", "Team"],
        turnovers_rating_get_dict("D"), defensemen_teams)
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
    

def run_played_game_parser_engine(game_types : str="R", game_list : dict={}):

    # loop through all gathered match dates until we have parsed all data
    sorted_date_list = sorted(game_list)

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
                    goalie_metrics = \
                        output_list["player_data"]['goalie_metrics']
                    utilization_add_match_data(
                        goalie_metrics['utilization'], "G") 
                    discipline_add_match_data(goalie_metrics['discipline'], "G") 
                    goalie_goals_against_add_match_data(
                        goalie_metrics['goals_against'])  
                    goalie_save_percentage_add_match_data(
                        goalie_metrics['save_percentage'])
                    goalie_save_consistency_add_match_data(
                        goalie_metrics['save_consistency'])
                    for goalie in goalie_metrics['utilization'].keys():
                        goalie_teams[goalie] = \
                            goalie_metrics['utilization'][goalie]['team']

                    # Forwards
                    forward_metrics = \
                        output_list['player_data']['forward_metrics']
                    utilization_add_match_data(forward_metrics['utilization'],
                        "C")
                    blocks_add_match_data(forward_metrics['blocks'], "C")
                    contributing_games_add_match_data(
                        forward_metrics['contributing_games'], "C")
                    discipline_add_match_data(forward_metrics['discipline'],
                        "C")
                    hitting_add_match_data(forward_metrics['hits'], "C")
                    plus_minus_add_match_data(forward_metrics['plus_minus'],
                        "C")
                    total_points_add_match_data(forward_metrics['total_points'],
                        "C")
                    turnovers_add_match_data(forward_metrics['turnovers'], "C")
                    multipoint_add_match_data(
                        forward_metrics['multipoint_games'], "C")
                    for forward in forward_metrics['utilization'].keys():
                        forward_teams[forward] = \
                            forward_metrics['utilization'][forward]['team']

                    # Defensemen
                    defensemen_metrics = \
                        output_list['player_data']['defensemen_metrics']
                    utilization_add_match_data(
                        defensemen_metrics['utilization'], "D")
                    blocks_add_match_data(defensemen_metrics['blocks'], "D")
                    contributing_games_add_match_data(
                        defensemen_metrics['contributing_games'], "D")
                    discipline_add_match_data(defensemen_metrics['discipline'],
                        "D")
                    hitting_add_match_data(defensemen_metrics['hits'], "D")
                    multipoint_add_match_data(
                        defensemen_metrics['multipoint_games'], "D")
                    plus_minus_add_match_data(defensemen_metrics['plus_minus'],
                        "D")
                    total_points_add_match_data(
                        defensemen_metrics['total_points'], "D")
                    turnovers_add_match_data(defensemen_metrics['turnovers'],
                        "D")
                    for defenseman in defensemen_metrics['utilization'].keys():
                        defensemen_teams[defenseman] = \
                            defensemen_metrics['utilization'][defenseman][
                                'team']
                        
                # teams
                else:
                    metric_data = output_list["team_data"]

                    ### clutch data ###
                    clutch_add_match_data(metric_data['clutch_data'])

                    ### defensive data ###
                    defensive_rating_add_match_data(
                        metric_data['defensive_data'])

                    ### offensive data ###
                    offensive_rating_add_match_data(
                        metric_data['offensive_data'])

                    ### recent form data ###
                    recent_form_add_match_data(metric_data['recent_form_data'])

                    ### strength of schedule data ###
                    strength_of_schedule_add_match_data(metric_data['sos_data'])
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
            plot_uncorrected_team_metrics(game_types)

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
            plot_corrected_team_metrics(game_types)

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
            plot_combined_team_metrics(game_types)
            

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
        apply_sigmoid_correction(utilization_rating_get_dict("G"))

        discipline_scale_by_utilization(utilization_rating_get_dict("G"), "G")

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

        contributing_games_scale_by_games(
            strength_of_schedule_get_games_played_dict(), forward_teams, "C")

        discipline_scale_by_utilization(utilization_rating_get_dict("C"), "C")

        hitting_scale_by_game(strength_of_schedule_get_games_played_dict(),
            forward_teams, "C")

        multipoint_scale_by_game(strength_of_schedule_get_games_played_dict(),
            forward_teams, "C")

        plus_minus_scale_by_utilization(utilization_rating_get_dict("C"), "C")

        total_points_scale_by_game(strength_of_schedule_get_games_played_dict(),
            forward_teams, "C")

        turnovers_scale_by_utilization(utilization_rating_get_dict("C"), "C")

        ### Defensemen ###
        utilization_scale_by_game(
            strength_of_schedule_get_games_played_dict(), defensemen_teams, "D")
        apply_sigmoid_correction(utilization_rating_get_dict("D"))

        blocks_scale_by_shots_against(
            defensive_rating_get_unscaled_shots_against_dict(),
            defensemen_teams, "D")
        
        contributing_games_scale_by_games(
            strength_of_schedule_get_games_played_dict(), defensemen_teams, "D")

        discipline_scale_by_utilization(utilization_rating_get_dict("D"), "D")

        hitting_scale_by_game(strength_of_schedule_get_games_played_dict(),
            defensemen_teams, "D")
        
        multipoint_scale_by_game(strength_of_schedule_get_games_played_dict(),
            defensemen_teams, "D")

        plus_minus_scale_by_utilization(utilization_rating_get_dict("D"), "D")

        total_points_scale_by_game(strength_of_schedule_get_games_played_dict(),
            defensemen_teams, "D")

        turnovers_scale_by_utilization(utilization_rating_get_dict("D"), "D")
        if final_date:
            print("Plot Player data before correction")
            plot_uncorrected_player_metrics(game_types)

        # Goalies
        apply_sigmoid_correction(discipline_rating_get_dict("G"))
        apply_sigmoid_correction(goalie_goals_against_get_dict(), True)
        apply_sigmoid_correction(goalie_save_percentage_get_dict())
        apply_sigmoid_correction(goalie_save_consistency_get_dict())

        # Forwards
        apply_sigmoid_correction(blocks_rating_get_dict("C"))
        apply_sigmoid_correction(contributing_games_rating_get_dict("C"))
        apply_sigmoid_correction(discipline_rating_get_dict("C"), True)
        apply_sigmoid_correction(hitting_rating_get_dict("C"))
        apply_sigmoid_correction(multipoint_rating_get_dict("C"))
        apply_sigmoid_correction(plus_minus_rating_get_dict("C"))
        apply_sigmoid_correction(total_points_rating_get_dict("C"))
        apply_sigmoid_correction(turnovers_rating_get_dict("C"))

        # Defensemen
        apply_sigmoid_correction(blocks_rating_get_dict("D"))
        apply_sigmoid_correction(contributing_games_rating_get_dict("D"))
        apply_sigmoid_correction(discipline_rating_get_dict("D"), True)
        apply_sigmoid_correction(hitting_rating_get_dict("D"))
        apply_sigmoid_correction(multipoint_rating_get_dict("D"))
        apply_sigmoid_correction(plus_minus_rating_get_dict("D"))
        apply_sigmoid_correction(total_points_rating_get_dict("D"))
        apply_sigmoid_correction(turnovers_rating_get_dict("D"))

        if final_date:
            print("Plot Player data after correction")
            plot_corrected_player_metrics(game_types)

        ### combine metrics to overall score and plot ###
        # Goalies
        for goalie in utilization_rating_get_dict("G").keys():
            goalie_total_rating[goalie] = (
                (utilization_rating_get_dict("G")[goalie] *
                    goalie_rating_weights.UTILIZATION_WEIGHT.value) +
                (discipline_rating_get_dict("G")[goalie] *
                    goalie_rating_weights.DISCIPLINE_WEIGHT.value) +
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
                (hitting_rating_get_dict("C")[forward] *
                    forward_rating_weights.HITS_WEIGHT.value) +
                (blocks_rating_get_dict("C")[forward] *
                    forward_rating_weights.SHOT_BLOCKING_WEIGHT.value) +
                (utilization_rating_get_dict("C")[forward] *
                    forward_rating_weights.UTILIZATION_WEIGHT.value) +
                (discipline_rating_get_dict("C")[forward] *
                    forward_rating_weights.DISIPLINE_WEIGHT.value) +
                (plus_minus_rating_get_dict("C")[forward] *
                    forward_rating_weights.PLUS_MINUS_WEIGHT.value) +
                (total_points_rating_get_dict("C")[forward] *
                    forward_rating_weights.POINTS_WEIGHT.value) +
                (turnovers_rating_get_dict("C")[forward] *
                    forward_rating_weights.TAKEAWAYS_WEIGHT.value) +
                (contributing_games_rating_get_dict("C")[forward] *
                    forward_rating_weights.CONTRIBUTION_WEIGHT.value) +
                (multipoint_rating_get_dict("C")[forward] *
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
                (hitting_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.HITS_WEIGHT.value) +
                (blocks_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.SHOT_BLOCKING_WEIGHT.value) +
                (utilization_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.UTILIZATION_WEIGHT.value) +
                (discipline_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.DISIPLINE_WEIGHT.value) +
                (plus_minus_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.PLUS_MINUS_WEIGHT.value) +
                (total_points_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.POINTS_WEIGHT.value) +
                (turnovers_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.TAKEAWAYS_WEIGHT.value) +
                (contributing_games_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.CONTRIBUTION_WEIGHT.value) +
                (multipoint_rating_get_dict("D")[defensemen] *
                    defensemen_rating_weights.MULTIPOINT_WEIGHT.value)
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
    (regular_season_matches, playoff_matches, upcoming_matches,
        upcoming_playoff_matches) = get_game_records(SEASON)
    print_time_diff(match_data_start, time.time())

    # automatically determine if the season is over based on the number of
    # unplayed matched found
    if len(upcoming_matches) == 0:
        print("Season Complete, Adding End Year Rankings\n")
        REG_SEASON_COMPLETE = True

    # if regular season games have been played then run post processing on those
    if len(regular_season_matches) > 0:
        print("Running Regular Season Post Process\n")
        run_played_game_parser_engine("R", regular_season_matches)

    # reset all stats to just isolate post season.
    clutch_rating_reset()
    defensive_rating_reset()
    offensive_rating_reset()
    recent_form_reset()
    strength_of_schedule_reset()

    blocks_reset()
    contributing_games_reset()
    discipline_reset()
    hitting_reset()
    multipoint_reset()
    plus_minus_reset()
    utilization_reset()
    total_points_reset()
    turnovers_reset()

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

    exit(0)

    REG_SEASON_COMPLETE = False

    # if playoffs have started then run post processing on those games
    if len(playoff_matches) > 0 :
        print("Running Post Season Post Process\n")
        run_played_game_parser_engine("P", playoff_matches)

    # if there are matches in the schedule that are still upcoming then process
    print_time_diff(start, time.time())
    start = time.time()

    if len(upcoming_matches) > 0:
        print("Running Post Season Match Predicter")
        run_upcoming_game_parser_engine()
    print_time_diff(start, time.time())
    exit(0)
