from multiprocessing import Process, Queue, freeze_support
import requests
import json
import time
import os
import csv
import datetime
from enum import Enum

# import all custom modules for parsing
from Team_Metrics.Average_Ranking_Parser import average_rankings_get_dict, \
    average_rankings_parse, average_ranking_get_ranking_dates, \
    average_rankings_update
from Team_Metrics.Absolute_Ranking_Parser import absolute_rankings_get_dict, \
    absolute_rankings_parse, absolute_rankings_update

# import all custom team modules for statistical analysis
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_rating_get_trend_dict, clutch_calculate_lead_protection, \
    clutch_add_match_data
from Team_Metrics.Defensive_Rating import defensive_rating_get_dict, \
    defensive_rating_get_shots_against_dict, \
    defensive_rating_get_unscaled_shots_against_dict, \
    defensive_rating_get_goals_against_dict, defensive_rating_get_pk_dict, \
    defensive_rating_get_trend_dict, defensive_rating_get_pk_oppertunities_dict, \
    defensive_rating_get_data_set, defensive_rating_add_match_data, \
    defensive_rating_calculate_all, defensive_rating_combine_metrics
from Team_Metrics.Offensive_Rating import offensive_rating_get_dict, \
    offensive_rating_get_shots_for_dict, offensive_rating_get_goals_for_dict, \
    offensive_rating_get_pp_dict, offensive_rating_get_trend_dict, \
    offensive_rating_get_pp_oppertunities_dict, offensive_rating_get_data_set, \
    offensive_rating_add_match_data, offensive_rating_calculate_power_play, \
    offensive_rating_combine_metrics
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_get_streak_dict, recent_form_get_last_10_dict, \
    recent_form_get_last_20_dict, recent_form_get_last_40_dict, \
    recent_form_get_trend_dict, recent_form_get_data_set, \
    recent_form_add_match_data, recent_form_calculate_all, \
    recent_form_combine_metrics 
from Team_Metrics.Strength_of_Schedule import strength_of_schedule_get_dict, \
    strength_of_schedule_get_games_played_dict, \
    strength_of_schedule_get_trend_dict, strength_of_schedule_get_data_set, \
    strength_of_schedule_add_match_data, strength_of_schedule_scale_by_game

# import all custom player modules for statistical analysis
### GOALIES
from Goalie_Metrics.Goalie_Utilization import goalie_utilization_get_dict, \
    goalie_utilization_get_data_set, goalie_utilization_add_match_data, \
    goalie_utilization_scale_by_game
from Goalie_Metrics.Goalie_Goals_Against import goalie_goals_against_get_dict, \
    goalie_goals_against_get_data_set, goalie_goals_against_add_match_data, \
    goalie_goals_against_scale_by_utilization
from Goalie_Metrics.Goalie_Save_Percentage import \
    goalie_save_percentage_get_dict, goalie_save_percentage_get_data_set, \
    goalie_save_percentage_add_match_data, goalie_save_percentage_calculate_all, \
    goalie_save_percentage_combine_metrics
from Goalie_Metrics.Goalie_Save_Consistency import \
    goalie_save_consistency_get_dict, goalie_save_consistency_get_data_set, \
    goalie_save_consistency_add_match_data, \
    goalie_save_consistency_scale_by_games

### FORWARDS
from Forward_Metrics.Forward_Blocks import forward_blocks_get_dict, \
    forward_blocks_get_data_set, forward_blocks_add_match_data, \
    forward_blocks_scale_by_shots_against
from Forward_Metrics.Forward_Contributing_Games import \
    forward_contributing_games_get_dict, \
    forward_contributing_games_get_data_set, \
    forward_contributing_games_add_match_data, \
    forward_contributing_games_scale_by_games
from Forward_Metrics.Forward_Discipline import \
    forward_discipline_get_dict, forward_discipline_get_data, \
    forward_discipline_add_match_data, forward_discipline_scale_by_utilization
from Forward_Metrics.Forward_Hits import \
    forward_hits_get_dict, forward_hits_get_data_set, \
    forward_hits_add_match_data, forward_hits_scale_by_games
from Forward_Metrics.Forward_Multipoint_Games import \
    forward_multipoint_games_get_dict, forward_multipoint_games_get_data_set, \
    forward_multipoint_games_add_match_data, forward_multipoint_games_scale_by_games
from Forward_Metrics.Forward_PlusMinus import \
    forward_plus_minus_get_dict, forward_plus_minus_get_data_set, \
    forward_plus_minus_add_match_data, forward_plus_minus_scale_by_utilization
from Forward_Metrics.Forward_Total_Points import \
    forward_points_get_dict, forward_points_get_data_set, \
    forward_points_add_match_data, forward_points_scale_by_games
from Forward_Metrics.Forward_Takeaways import \
    forward_takeaways_get_dict, forward_takeaways_get_data_set, \
    forward_takeaways_add_match_data, forward_takeaways_scale_by_utilization
from Forward_Metrics.Forward_Utilization import \
    forward_utilization_get_dict, forward_utilization_get_even_time_dict, \
    forward_utilization_get_pp_time_dict, \
    forward_utilization_get_pk_time_dict, forward_utilization_get_data_set, \
    forward_utilization_add_match_data, forward_utilization_scale_all, \
    forward_utilization_combine_metrics

### DEFENSEMEN
from Defensemen_Metrics.Defensemen_Blocks import defensemen_blocks_get_dict, \
    defensemen_blocks_get_data_set, defensemen_blocks_add_match_data, \
    defensemen_blocks_scale_by_shots_against
from Defensemen_Metrics.Defensemen_Discipline import \
    defensemen_discipline_get_dict, defensemen_discipline_get_data, \
    defensemen_discipline_add_match_data, defensemen_discipline_scale_by_utilization
from Defensemen_Metrics.Defensemen_Hits import \
    defensemen_hits_get_dict, defensemen_hits_get_data_set, \
    defensemen_hits_add_match_data, defensemen_hits_scale_by_games
from Defensemen_Metrics.Defensemen_PlusMinus import \
    defensemen_plus_minus_get_dict, defensemen_plus_minus_get_data_set, \
    defensemen_plus_minus_add_match_data, \
    defensemen_plus_minus_scale_by_utilization
from Defensemen_Metrics.Defensemen_Points import \
    defensemen_points_get_dict, defensemen_points_get_data_set, \
    defensemen_points_add_match_data, defensemen_points_scale_by_games
from Defensemen_Metrics.Defensemen_Takeaways import \
    defensemen_takeaways_get_dict, defensemen_takeaways_get_data_set, \
    defensemen_takeaways_add_match_data, \
    defensemen_takeaways_scale_by_utilization
from Defensemen_Metrics.Defensemen_Utilization import \
    defensemen_utilization_get_dict, defensemen_utilization_get_even_time_dict, \
    defensemen_utilization_get_pp_time_dict, \
    defensemen_utilization_get_pk_time_dict, \
    defensemen_utilization_get_data_set, defensemen_utilization_add_match_data, \
    defensemen_utilization_scale_all, defensemen_utilization_combine_metrics


# shared engine tools
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import total_rating_weights, goalie_rating_weights, \
    forward_rating_weights, defensemen_rating_weights
from Plotter import plot_data_set, plot_trend_set, plot_player_ranking
from CSV_Writer import write_out_file, update_trend_file, write_out_player_file


sigmoid_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


total_rating = {}


total_rating_trend = {
    'Anaheim Ducks' : [],
    'Arizona Coyotes' : [],
    'Boston Bruins' : [],
    'Buffalo Sabres' : [],
    'Calgary Flames' : [],
    'Carolina Hurricanes' : [],
    'Chicago Blackhawks' : [],
    'Colorado Avalanche' : [],
    'Columbus Blue Jackets' : [],
    'Dallas Stars' : [],
    'Detroit Red Wings' : [],
    'Edmonton Oilers' : [],
    'Florida Panthers' : [],
    'Los Angeles Kings' : [],
    'Minnesota Wild' : [],
    'Montréal Canadiens' : [],
    'Nashville Predators' : [],
    'New Jersey Devils' : [],
    'New York Islanders' : [],
    'New York Rangers' : [],
    'Ottawa Senators' : [],
    'Philadelphia Flyers' : [],
    'Pittsburgh Penguins' : [],
    'San Jose Sharks' : [],
    'Seattle Kraken' : [],
    'St. Louis Blues' : [],
    'Tampa Bay Lightning' : [],
    'Toronto Maple Leafs' : [],
    'Vancouver Canucks' : [],
    'Vegas Golden Knights' : [],
    'Washington Capitals' : [],
    'Winnipeg Jets' : [],
}


average_goalie_rating = {}


average_forward_rating = {}


average_defenseman_rating = {}


average_player_rating = {}


season_matches = {}


goalie_teams = {}


forward_teams = {}


defensemen_teams = {}


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


def parse_trend_file(file_name, trend_dict) -> dict:
    header_row = True

    # open the average rating file
    with open(file_name, newline='') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for rating in ratings:
            if header_row:
                header_row = False
                continue

            if len(rating) == 0:
                continue

            # special case for the canadians french spelling
            if rating[1] == 'MontrÃ©al Canadiens':
                trend_dict['Montréal Canadiens'].append(float(rating[3]))
                continue

            # for every team, add the rating for that week
            trend_dict[rating[1]].append(float(rating[3]))


def parse_all_data_files() -> None:
    average_rankings_parse(
        'Output_Files/Team_Files/Trend_Files/AverageRankings.csv')
    absolute_rankings_parse(
        'Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv')
    parse_trend_file('Output_Files/Team_Files/Trend_Files/ClutchRating.csv',
        clutch_rating_get_trend_dict())
    parse_trend_file('Output_Files/Team_Files/Trend_Files/DefensiveRating.csv',
        defensive_rating_get_trend_dict())
    parse_trend_file('Output_Files/Team_Files/Trend_Files/OffensiveRating.csv',
        offensive_rating_get_trend_dict())
    parse_trend_file('Output_Files/Team_Files/Trend_Files/RecentForm.csv',
        recent_form_get_trend_dict())
    parse_trend_file(
        'Output_Files/Team_Files/Trend_Files/StrengthOfSchedule.csv',
        strength_of_schedule_get_trend_dict())
    parse_trend_file(
        'Output_Files/Team_Files/Trend_Files/RatingScore.csv',
        total_rating_trend)


def print_time_diff(start_time : float=0.0, end_time : float=0.0) -> None:
    print("Completed in {} seconds".format(end_time - start_time))


def parse_web_match_data(game_date : dict={}) -> list:
    game_data = []
    for game in game_date["games"]:

        # if the game is a completed regular season game then add to list
        if (game["status"]["abstractGameState"] == "Final"):
            box_score = \
                "https://statsapi.web.nhl.com/api/v1/game/" + \
                    "{}/boxscore".format(game["gamePk"])
            box_score_web_data = requests.get(box_score)
            box_score_parsed_data = json.loads(box_score_web_data.content)
            game_data.append({'date':game_date["date"],
                'boxscore':box_score_parsed_data,
                'linescore':game})
        else:
            return game_data
    return game_data


def get_game_records() -> None:
    schedule = \
        "https://statsapi.web.nhl.com/api/v1/schedule?season=20222023" + \
            "&gameType=R&expand=schedule.linescore"
    schedule_web_data = requests.get(schedule)
    schedule_parsed_data = json.loads(schedule_web_data.content)

    match_parser_process_list = []
    for i in range(15):
        match_parser_process_list.append(Process(target=worker_node,
            args=(match_input_queue, match_output_queue,
                i)))
    for process in match_parser_process_list:
        process.start()

    # matches are orginized by date they take place
    for date in schedule_parsed_data["dates"]:

        # # Skip this date if all the games arn't finished yet
        if date["games"][0]["status"]["abstractGameState"] != "Final":
            break

        # for each game on a specific date loop through
        match_input_queue.put((parse_web_match_data, ([date])))

    for i in range(15):
        match_input_queue.put('STOP')
    for i in range(15):
        for output_list in iter(match_output_queue.get, 'STOP'):
            if (output_list is not None) and (len(output_list) > 0):
                season_matches[output_list[0]['date']] = output_list
    for process in match_parser_process_list:
        process.join()


def worker_node(input_queue : Queue=None, output_queue : Queue=None,
                id : int=0) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    print("Exiting! Worker {} ran {} jobs".format(id, i))
    output_queue.put('STOP')


def run_team_match_parsers() -> None:

    # get all the different parsed trend data dictionaries
    #clutch_trends = clutch_rating_get_trend_dict()
    defensive_trends = defensive_rating_get_trend_dict()
    offensive_trends = offensive_rating_get_trend_dict()
    #recent_form_trends = recent_form_get_trend_dict()
    sos_trends = strength_of_schedule_get_trend_dict()
    date_count = 0
    final_period = False
    current_rating_period = average_ranking_get_ranking_dates()[date_count]
    next_rating_period = average_ranking_get_ranking_dates()[date_count + 1]

    # roll through all the dates updating the trend data when a different
    # ranking marker is reached
    for date in season_matches:
        parsed_date = date.split("-")
        parsed_date = datetime.date(int(parsed_date[0]), int(parsed_date[1]),
            int(parsed_date[2]))
        for match in season_matches[date]:
            
            # get the home and away team
            away_team = match['linescore']["teams"]["away"]["team"]["name"]
            home_team = match['linescore']["teams"]["home"]["team"]["name"]

            # if the game took place before any rankings were available just
            # give perfect scores to both teams for weighting
            if parsed_date < current_rating_period:
                clutch_stats = [1.0, 1.0]
                defensive_stats = [1.0, 1.0]
                offensive_stats = [1.0, 1.0]
                recent_form_stats = [1.0, 1.0]
                sos_stats = [1.0, 1.0]
                total_rating_stats = [1.0, 1.0]

            # otherwise find the correct scale factors for each team
            else:

                # if the next ranking period has been reached, and this is not
                # the last known rank, then update the current and next
                # markers and then keep going
                if parsed_date >= next_rating_period and final_period is False:
                    date_count += 1
                    current_rating_period = next_rating_period
                    if date_count + 1 <= \
                        len(average_ranking_get_ranking_dates()) - 1:
                        next_rating_period = \
                            average_ranking_get_ranking_dates()[date_count + 1]
                    else:
                        final_period = True

                # clutch trends don't really counter eachother so pass total
                # rating score to scale instead
                clutch_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]
                defensive_stats = [
                    defensive_trends[home_team][date_count],
                    defensive_trends[away_team][date_count]
                ]
                offensive_stats = [
                    offensive_trends[home_team][date_count],
                    offensive_trends[away_team][date_count]
                ]
                # recent form is too variable right now to be used to scale
                # for now just use the total rating score for the opposing team
                recent_form_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]
                sos_stats = [
                    sos_trends[home_team][date_count],
                    sos_trends[away_team][date_count]
                ]
                total_rating_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]

            # feed the match information with the scale factors for each team
            # into the match parser which will call all metrics to get all
            # relevant information required
            match_input_queue.put((parse_team_match_data,
                (match, [clutch_stats, defensive_stats, offensive_stats,
                    recent_form_stats, sos_stats, total_rating_stats])))
            

def run_player_match_parser() -> None:

    # get all the different parsed trend data dictionaries
    #clutch_trends = clutch_rating_get_trend_dict()
    defensive_trends = defensive_rating_get_trend_dict()
    offensive_trends = offensive_rating_get_trend_dict()
    #recent_form_trends = recent_form_get_trend_dict()
    sos_trends = strength_of_schedule_get_trend_dict()
    date_count = 0
    final_period = False
    current_rating_period = average_ranking_get_ranking_dates()[date_count]
    next_rating_period = average_ranking_get_ranking_dates()[date_count + 1]

    # roll through all the dates updating the trend data when a different
    # ranking marker is reached
    for date in season_matches:
        parsed_date = date.split("-")
        parsed_date = datetime.date(int(parsed_date[0]), int(parsed_date[1]),
            int(parsed_date[2]))
        for match in season_matches[date]:
            
            # get the home and away team
            away_team = match['linescore']["teams"]["away"]["team"]["name"]
            home_team = match['linescore']["teams"]["home"]["team"]["name"]

            # if the game took place before any rankings were available just
            # give perfect scores to both teams for weighting
            if parsed_date < current_rating_period:
                clutch_stats = [1.0, 1.0]
                defensive_stats = [1.0, 1.0]
                offensive_stats = [1.0, 1.0]
                recent_form_stats = [1.0, 1.0]
                sos_stats = [1.0, 1.0]
                total_rating_stats = [1.0, 1.0]

            # otherwise find the correct scale factors for each team
            else:

                # if the next ranking period has been reached, and this is not
                # the last known rank, then update the current and next
                # markers and then keep going
                if parsed_date >= next_rating_period and final_period is False:
                    date_count += 1
                    current_rating_period = next_rating_period
                    if date_count + 1 <= \
                        len(average_ranking_get_ranking_dates()) - 1:
                        next_rating_period = \
                            average_ranking_get_ranking_dates()[date_count + 1]
                    else:
                        final_period = True

                # clutch trends don't really counter eachother so pass total
                # rating score to scale instead
                clutch_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]
                defensive_stats = [
                    defensive_trends[home_team][date_count],
                    defensive_trends[away_team][date_count]
                ]
                offensive_stats = [
                    offensive_trends[home_team][date_count],
                    offensive_trends[away_team][date_count]
                ]
                # recent form is too variable right now to be used to scale
                # for now just use the total rating score for the opposing team
                recent_form_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]
                sos_stats = [
                    sos_trends[home_team][date_count],
                    sos_trends[away_team][date_count]
                ]
                total_rating_stats = [
                    total_rating_trend[home_team][date_count],
                    total_rating_trend[away_team][date_count]
                ]

            # feed the match information with the scale factors for each team
            # into the match parser which will call all metrics to get all
            # relevant information required
            # while in the game sort player data
            # start with home team players"]
            goalies = {}
            forwards = {}
            defensemen = {}
            players = match['boxscore']["teams"]["home"]["players"]
            for player_by_ID in players:

                # find the players position
                # if we can't determine the position, skip getting stats
                position = players[player_by_ID]["person"].get(
                    "primaryPosition")
                if position is not None:
                    position = position["type"]
                else:
                    position = players[player_by_ID]["position"]["type"]
                if position == "Unknown":
                    continue

                # read out the players name
                name = players[player_by_ID]["person"]["fullName"]

                # determine if the player had any stats for this game
                if "skaterStats" in players[player_by_ID]["stats"]:
                    stats = players[player_by_ID]["stats"]["skaterStats"]
                elif "goalieStats" in players[player_by_ID]["stats"]:
                    stats = players[player_by_ID]["stats"]["goalieStats"]
                else:
                    stats = None

                # sort all the players in this match to parse their data
                if (position == 'Goalie') and (stats != None):
                    goalies[name] = [home_team, stats]
                elif (position == 'Forward') and (stats != None):
                    forwards[name] = [home_team, stats]
                elif (stats != None):
                    defensemen[name] = [home_team, stats]

            # then do away team players
            players = match['boxscore']["teams"]["away"]["players"]
            for player_by_ID in players:

                # find the players position
                # if we can't determine the position, skip getting stats
                position = players[player_by_ID]["person"].get(
                    "primaryPosition")
                if position is not None:
                    position = position["type"]
                else:
                    position = players[player_by_ID]["position"]["type"]
                if position == "Unknown":
                    continue

                # read out the players name
                name = players[player_by_ID]["person"]["fullName"]

                # determine if the player had any stats for this game
                if "skaterStats" in players[player_by_ID]["stats"]:
                    stats = players[player_by_ID]["stats"]["skaterStats"]
                elif "goalieStats" in players[player_by_ID]["stats"]:
                    stats = players[player_by_ID]["stats"]["goalieStats"]
                else:
                    stats = None

                # sort all the players in this match to parse their data
                if (position == 'Goalie') and (stats != None):
                    goalies[name] = [away_team, stats]
                elif (position == 'Forward') and (stats != None):
                    forwards[name] = [away_team, stats]
                elif (stats != None):
                    defensemen[name] = [away_team, stats]

            # feed the match information with the scale factors for each team
            # into the match parser which will call all metrics to get all
            # relevant information required
            match_input_queue.put((parse_player_match_data,
                (match, [clutch_stats, defensive_stats, offensive_stats,
                    recent_form_stats, sos_stats, total_rating_stats],
                [goalies, forwards, defensemen])))


def parse_team_match_data(match_data : dict={}, relative_metrics : list=[]) \
                                                                        -> list:
    metric_data = []

    # get home and away team
    home_team = match_data["linescore"]["teams"]["home"]["team"]["name"]
    away_team = match_data["linescore"]["teams"]["away"]["team"]["name"]

    ### clutch rating ###
    clutch_data = clutch_calculate_lead_protection(match_data)
    clutch_data[0][home_team] *= relative_metrics[Metric_Order.CLUTCH.value][
        Team_Selection.HOME.value]
    clutch_data[1][away_team] *= relative_metrics[Metric_Order.CLUTCH.value][
        Team_Selection.AWAY.value]
    metric_data.append(clutch_data)

    ### defensive rating ###
    # shots against
    defensive_data = defensive_rating_get_data_set(match_data)
    defensive_data[0][home_team] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[0][away_team] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    
    # goals against
    defensive_data[1][home_team] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[1][away_team] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    
    # penalty kill oppertunities
    defensive_data[2][home_team][0] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[2][away_team][0] /= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    metric_data.append(defensive_data)

    ### offensive rating ###
    # shots for
    offensive_data = offensive_rating_get_data_set(match_data)
    offensive_data[0][home_team] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    offensive_data[0][away_team] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]

    # goals for
    offensive_data[1][home_team] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    offensive_data[1][away_team] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]

    # power play oppertunities
    offensive_data[2][home_team][0] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.AWAY.value]
    offensive_data[2][away_team][0] *= \
        relative_metrics[Metric_Order.DEFENSIVE.value][
            Team_Selection.HOME.value]
    metric_data.append(offensive_data)

    ### recent form ###
    recent_form_data = recent_form_get_data_set(match_data)
    recent_form_data[1][home_team] *= \
        relative_metrics[Metric_Order.RECENT.value][
            Team_Selection.AWAY.value]
    recent_form_data[1][away_team] *= \
        relative_metrics[Metric_Order.RECENT.value][
            Team_Selection.HOME.value]
    metric_data.append(recent_form_data)

    ### strength of schedule
    sos_data = strength_of_schedule_get_data_set(match_data)
    sos_data[home_team] *= \
        relative_metrics[Metric_Order.SOS.value][Team_Selection.AWAY.value]
    sos_data[away_team] *= \
        relative_metrics[Metric_Order.SOS.value][Team_Selection.HOME.value]
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
    home_team = match_data["linescore"]["teams"]["home"]["team"]["name"]

    ### Goalie Stats ###
    goalie_utilization_data = goalie_utilization_get_data_set(goalies)
    goalie_goals_against_data = goalie_goals_against_get_data_set(goalies)
    goalie_save_per_data = goalie_save_percentage_get_data_set(goalies)
    goalie_save_consistency_data = goalie_save_consistency_get_data_set(goalies)

    # unlike team engine, run all relative scaling at the end of the section
    for goalie in goalies:

        # if the player is on the home team
        if goalies[goalie][0] == home_team:

            # Utilization
            goalie_utilization_data[goalie][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.AWAY.value])
            
            # Goals Against
            goalie_goals_against_data[goalie][1] *= \
                (1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Save Percentage
            goalie_save_per_data[1][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            goalie_save_per_data[2][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            goalie_save_per_data[3][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
            
            # Save Consistency
            goalie_save_consistency_data[goalie][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.AWAY.value])
        else:

            # Utilization
            goalie_utilization_data[goalie][1] *= \
                (1 + relative_metrics[Metric_Order.TOTAL.value][
                    Team_Selection.HOME.value])
            
            # Goals Against
            goalie_goals_against_data[goalie][1] *= \
                (1 - relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Save Percentage
            goalie_save_per_data[1][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            goalie_save_per_data[1][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            goalie_save_per_data[1][goalie][0] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
            
            # Save Consistency
            goalie_save_consistency_data[goalie][1] *= \
                (1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                    Team_Selection.HOME.value])
    
    # Append Goalie metrics
    goalie_metrics.append(goalie_utilization_data)
    goalie_metrics.append(goalie_goals_against_data)
    goalie_metrics.append(goalie_save_per_data)
    goalie_metrics.append(goalie_save_consistency_data)

    ### Forward metrics
    forward_blocks_data = forward_blocks_get_data_set(forwards)
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
    forward_utilization_data = forward_utilization_get_data_set(
        forwards)
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
    defensemen_blocks_data = defensemen_blocks_get_data_set(defensemen)
    defensemen_discipline_data = defensemen_discipline_get_data(defensemen)
    defensemen_utilization_data = defensemen_utilization_get_data_set(
        defensemen)
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


def plot_uncorrected_team_metrics() -> None:

    ### Clutch Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ClutchRatingBase.csv",
        ["Team", "Clutch Rating Base"], clutch_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ClutchRatingBase.csv",
        ["Team", "Clutch Rating Base"], 0.0, 0.0, [],
        "Graphs/Teams/Clutch_Rating/clutch_rating_base.png")))

    ### Defensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"],
        defensive_rating_get_shots_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"],
        defensive_rating_get_goals_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], defensive_rating_get_pk_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/penalty_kill_base.png")))

    ### Offensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], offensive_rating_get_shots_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], offensive_rating_get_goals_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], offensive_rating_get_pp_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/power_play_base.png")))

    ### Recent Form ###
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], recent_form_get_streak_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], 0.0, 0.0, [],
        "Graphs/Teams/Recent_Form/recent_form_streak_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Teams/Recent_Form/recent_form_last_ten_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], 20.0, 0,
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "Graphs/Teams/Recent_Form/recent_form_last_twenty_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], 40.0, 0,
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40],
        "Graphs/Teams/Recent_Form/recent_form_last_fourty_base.png")))

    ### Strength of Schedule
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], strength_of_schedule_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], 0.0, 0.0, [],
        "Graphs/Teams/Strength_of_Schedule/sos_base.png")))
    strength_of_schedule_scale_by_game()
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleScale.csv",
        ["Team", "Strength of Schedule Game Scale"], strength_of_schedule_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleScale.csv",
        ["Team", "Strength of Schedule Game Scale"], 0.0, 0.0, [],
        "Graphs/Teams/Strength_of_Schedule/sos_game_scale.png")))


def plot_corrected_team_metrics() -> None:

    ### Clutch Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], clutch_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/clutch_rating_final.png")))

    ### Defensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"],
        defensive_rating_get_shots_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"],
        defensive_rating_get_goals_against_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], defensive_rating_get_pk_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/penalty_kill_sigmoid.png")))

    ### Offensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], offensive_rating_get_shots_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], offensive_rating_get_goals_for_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], offensive_rating_get_pp_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/power_play_sigmoid.png")))

    ### Recent Form ###
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"], recent_form_get_streak_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_streak_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_ten_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_twenty_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_fourty_corrected.png")))

    ### Strength of Schedule ###
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"],
        strength_of_schedule_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Strength_of_Schedule/strenght_of_schedule_final.png")))
    

def plot_uncorrected_player_metrics() -> None:

    ### Goalies
    # Utilization
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Base.csv",
        ["Goalie", "Utilization Base", "Team"], goalie_utilization_get_dict(),
        goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Base.csv",
        ["Goalie", "Utilization Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Utilization/utilization_base.png")))
    
    # Goals Against
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base", "Team"],
        goalie_goals_against_get_dict(), goalie_teams, False)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Base.csv",
        ["Goalie", "Goals Against Avg Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Goals_Against/goals_against_base.png", True)))
    
    # Save Percentage
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled", "Team"],
        goalie_save_percentage_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Weighted.csv",
        ["Goalie", "Save Percentage Scaled"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Percentage/save_percentage_scaled.png")))
    
    # Save Consistency
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Consistency_Base.csv",
        ["Goalie", "Save Consistency Base", "Team"],
        goalie_save_consistency_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Consistency_Base.csv",
        ["Goalie", "Save Consistency Base"], 0.0, 0.0, [],
        "Graphs/Goalies/Save_Consistency/save_consistency_base.png")))
    
    ### Forwards
    # Blocks
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Blocks_Base.csv",
        ["Forward", "Blocks Base", "Team"],
        forward_blocks_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Blocks_Base.csv",
        ["Forward", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Forward/Blocks/blocks_base.png")))
    
    # Contributing Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Contribution_Base.csv",
        ["Forward", "Contribution Base", "Team"],
        forward_contributing_games_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Contribution_Base.csv",
        ["Forward", "Contribution Base"], 0.0, 0.0, [],
        "Graphs/Forward/Contribution/contribution_base.png")))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Discipline_Base.csv",
        ["Forward", "Discipline Base", "Team"],
        forward_discipline_get_dict(), forward_teams, False)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Discipline_Base.csv",
        ["Forward", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Forward/Discipline/discipline_base.png", True)))
    
    # Hits
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Hits_Base.csv",
        ["Forward", "Hits Base", "Team"],
        forward_hits_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Hits_Base.csv",
        ["Forward", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Forward/Hits/hits_base.png", False)))
    
    # Multipoint Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Multipoint_Base.csv",
        ["Forward", "Multipoint Base", "Team"],
        forward_multipoint_games_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Multipoint_Base.csv",
        ["Forward", "Multipoint Base"], 0.0, 0.0, [],
        "Graphs/Forward/Multipoint/Multipoint_base.png", False)))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base", "Team"],
        forward_plus_minus_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Forward", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Forward/Plus_Minus/plus_minus_base.png", False)))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Takeaways_Base.csv",
        ["Forward", "Takeaways Base", "Team"],
        forward_takeaways_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Takeaways_Base.csv",
        ["Forward", "Takeaways Base"], 0.0, 0.0, [],
        "Graphs/Forward/Takeaways/takeaways_base.png", False)))
    
    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Total_Points_Base.csv",
        ["Forward", "Points Base", "Team"],
        forward_points_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Total_Points_Base.csv",
        ["Forward", "Points Base"], 0.0, 0.0, [],
        "Graphs/Forward/Total_Points/total_points_base.png", False)))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base", "Team"],
        forward_utilization_get_even_time_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Forward", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/even_utilzation_base.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Base.csv",
        ["Forward", "Power Play Utilization Base", "Team"],
        forward_utilization_get_pp_time_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PPUtilization_Base.csv",
        ["Forward", "Power Play Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/pp_utilization_base.png", False)))
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Base.csv",
        ["Forward", "Penalty Kill Utilization Base", "Team"],
        forward_utilization_get_pk_time_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/PKUtilization_Base.csv",
        ["Forward", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
        "Graphs/Forward/Utilization/pk_utilization_base.png", False)))
    
    ### Defensemen
    # Blocks
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Base.csv",
        ["Defensemen", "Blocks Base", "Team"],
        defensemen_blocks_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Base.csv",
        ["Defensemen", "Blocks Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Blocks/blocks_base.png")))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Base.csv",
        ["Defensemen", "Discipline Base", "Team"],
        defensemen_discipline_get_dict(), defensemen_teams, False)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Base.csv",
        ["Defensemen", "Discipline Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Discipline/discipline_base.png", True)))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base", "Team"],
        defensemen_utilization_get_even_time_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/EvnUtilization_Base.csv",
        ["Defensemen", "Even Strength Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/even_utilzation_base.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Base.csv",
        ["Defensemen", "Power Play Utilization Base", "Team"],
        defensemen_utilization_get_pp_time_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PPUtilization_Base.csv",
        ["Defensemen", "Power Play Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/pp_utilization_base.png", False)))
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Base.csv",
        ["Defensemen", "Penalty Kill Utilization Base", "Team"],
        defensemen_utilization_get_pk_time_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/PKUtilization_Base.csv",
        ["Defensemen", "Penalty Kill Utilization Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Utilization/pk_utilization_base.png", False)))
    
    # Hits
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Base.csv",
        ["Defensemen", "Hits Base", "Team"],
        defensemen_hits_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Base.csv",
        ["Defensemen", "Hits Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Hits/hits_base.png", False)))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base", "Team"],
        defensemen_plus_minus_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Base.csv",
        ["Defensemen", "Plus_Minus Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Plus_Minus/plus_minus_base.png", False)))
    
    # Points
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Points_Base.csv",
        ["Defensemen", "Points Base", "Team"],
        defensemen_points_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Points_Base.csv",
        ["Defensemen", "Points Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Points/points_base.png", False)))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Takeaways_Base.csv",
        ["Defensemen", "Takeaways Base", "Team"],
        defensemen_takeaways_get_dict(), defensemen_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Takeaways_Base.csv",
        ["Defensemen", "Takeaways Base"], 0.0, 0.0, [],
        "Graphs/Defensemen/Takeaways/takeaways_base.png", False)))


def plot_corrected_player_metrics() -> None:

    ### Goalies
    # Utilization
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected", "Team"],
        goalie_utilization_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Utilization_Corr.csv",
        ["Goalie", "Utilization Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Utilization/utilization_corrected.png")))
    
    # Goals Against
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected", "Team"],
        goalie_goals_against_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Goals_Against_Corrected.csv",
        ["Goalie", "Goals Against Avg Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goals_Against/goals_against_corrected.png")))
    
    # Save Percentage
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected", "Team"],
        goalie_save_percentage_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Percentage_Corrected.csv",
        ["Goalie", "Save Percentage Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Percentage/save_percentage_corrected.png")))
    
    # Save Consistency
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected", "Team"],
        goalie_save_consistency_get_dict(), goalie_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Goalie_Files/Instance_Files/Save_Consistency_Corr.csv",
        ["Goalie", "Save Consistency Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Save_Consistency/save_consistency_corrected.png")))
    
    ### Forwards
    # Blocks
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Blocks_Corrected.csv",
        ["Forward", "Blocks Corrected", "Team"],
        forward_blocks_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Blocks_Corrected.csv",
        ["Forward", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Blocks/blocks_corrected.png")))
    
    # Contributing Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Contribution_Corrected.csv",
        ["Forward", "Contribution Corrected", "Team"],
        forward_contributing_games_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Contribution_Corrected.csv",
        ["Forward", "Contribution Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Contribution/contribution_corrected.png")))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Discipline_Corrected.csv",
        ["Forward", "Discipline Corrected", "Team"],
        forward_discipline_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Discipline_Corrected.csv",
        ["Forward", "Discipline Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Discipline/discipline_corrected.png")))
    
    # Hits
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Hits_Corrected.csv",
        ["Forward", "Hits Corrected", "Team"],
        forward_hits_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Hits_Corrected.csv",
        ["Forward", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Hits/hits_corrected.png")))
    
    # Multipoint Games
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Multipoint_Corrected.csv",
        ["Forward", "Multipoint Corrected", "Team"],
        forward_multipoint_games_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Multipoint_Corrected.csv",
        ["Forward", "Multipoint Corrected"], 0.0, 0.0, [],
        "Graphs/Forward/Multipoint/multipoint_corrected.png", False)))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected", "Team"],
        forward_plus_minus_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Forward", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Plus_Minus/plus_minus_corrected.png")))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Takeaways_Corrected.csv",
        ["Forward", "Takeaways Corrected", "Team"],
        forward_takeaways_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Takeaways_Corrected.csv",
        ["Forward", "Takeaways Corrected"], 0.0, 0.0, [],
        "Graphs/Forward/Takeaways/takeaways_corrected.png", False)))
    
    # Total Points
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/Total_Points_Corrected.csv",
        ["Forward", "Points Corrected", "Team"],
        forward_points_get_dict(), forward_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/Total_Points_Corrected.csv",
        ["Forward", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Total_Points/total_points_corrected.png")))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/UtilizationRating.csv",
        ["Forward", "Utilization Rating", "Team"],
        forward_utilization_get_dict(), forward_teams, True)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Forward_Files/Instance_Files/UtilizationRating.csv",
        ["Forward", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Utilization/utilization_rating.png", False)))

    ### Defensemen
    # Blocks
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected", "Team"],
        defensemen_blocks_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Blocks_Corrected.csv",
        ["Defensemen", "Blocks Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Blocks/blocks_corrected.png")))
    
    # Discipline
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected", "Team"],
        defensemen_discipline_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Discipline_Corrected.csv",
        ["Defensemen", "Discipline Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Discipline/discipline_corrected.png")))
    
    # Hits
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected", "Team"],
        defensemen_hits_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Hits_Corrected.csv",
        ["Defensemen", "Hits Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Hits/hits_corrected.png")))
    
    # Plus Minus
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected", "Team"],
        defensemen_plus_minus_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Plus_Minus_Corrected.csv",
        ["Defensemen", "Plus_Minus Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Plus_Minus/plus_minus_corrected.png")))
    
    # Points
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Points_Corrected.csv",
        ["Defensemen", "Points Corrected", "Team"],
        defensemen_points_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Points_Corrected.csv",
        ["Defensemen", "Points Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Points/points_corrected.png")))
    
    # Takeaways
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/Takeaways_Corrected.csv",
        ["Defensemen", "Takeaways Corrected", "Team"],
        defensemen_takeaways_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/Takeaways_Corrected.csv",
        ["Defensemen", "Takeaways Corrected"], 0.0, 0.0, [],
        "Graphs/Defensemen/Takeaways/takeaways_corrected.png")))
    
    # Utilization
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/UtilizationRating.csv",
        ["Defensemen", "Utilization Rating", "Team"],
        defensemen_utilization_get_dict(), defensemen_teams)
    plotting_queue.put((plot_player_ranking, (
        "Output_Files/Defensemen_Files/Instance_Files/UtilizationRating.csv",
        ["Defensemen", "Utilization Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Utilization/utilization_rating.png")))


def combine_all_team_factors(update_trends : bool=True) -> None:
    
    # calculate the final rating for all teams using the forms above
    for team in clutch_rating_get_dict().keys():
        total_rating[team] = \
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
            

    # write out and plot the total ratings
    write_out_file("Output_Files/Team_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], total_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/final_rating_score.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/RatingScore.csv",
            total_rating)
    plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/RatingScore.csv",
        ["Rating Date", "Rating Score"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/rating_score_trend.png")))
    

def run_team_engine():

    # create a few match parsing processes to speed things up a bit
    subprocess_count = 15
    metric_process_list = []
    for i in range(subprocess_count):
        metric_process_list.append(Process(target=worker_node,
            args=(match_input_queue, match_output_queue,
                i)))
    for process in metric_process_list:
        process.start()

    # feed in matches until all completed matches this season have been put into
    # a process to be parsed
    match_parsing_start = time.time()
    print("Feeding in matches to workers")
    run_team_match_parsers()
    
    # let the metric workers know there are no more matches
    for i in range(subprocess_count):
        match_input_queue.put('STOP')
    
    # keep reading the metric output queue until all data is returned
    print("Combining jobs from worker nodes")
    for i in range(subprocess_count):
        for output_list in iter(match_output_queue.get, 'STOP'):

            ### clutch data ###
            clutch_return = output_list[Metric_Order.CLUTCH.value]
            clutch_add_match_data(clutch_return)

            ### defensive data ###
            defensive_return = output_list[Metric_Order.DEFENSIVE.value]
            defensive_rating_add_match_data(defensive_return)

            ### offensive data
            offensive_return = output_list[Metric_Order.OFFENSIVE.value]
            offensive_rating_add_match_data(offensive_return)

            ### recent form data
            recent_form_return = output_list[Metric_Order.RECENT.value]
            recent_form_add_match_data(recent_form_return)

            ### strength of schedule data ###
            sos_return = output_list[Metric_Order.SOS.value]
            strength_of_schedule_add_match_data(sos_return)
    for process in metric_process_list:
        process.join()

    # call any cleanup calculations required
    defensive_rating_calculate_all()
    offensive_rating_calculate_power_play()
    recent_form_calculate_all()
    print_time_diff(match_parsing_start, time.time())

    # now start the processes for plotting
    plotting_process_list = []
    for i in range(subprocess_count):
        plotting_process_list.append(Process(target=worker_node,
            args=(plotting_queue, dummy_queue, i)))
    for process in plotting_process_list:
        process.start()

    # write out any plots before sigmoid correction
    print("Plot data before correction")
    plot_uncorrected_team_metrics()

    ### apply all sigmoid corrections ###
    print("Apply corrections")
    sigmoid_start = time.time()

    # Clutch Rating
    apply_sigmoid_correction(clutch_rating_get_dict())

    # Defensive Rating
    apply_sigmoid_correction(defensive_rating_get_shots_against_dict(), True)
    apply_sigmoid_correction(defensive_rating_get_goals_against_dict(), True)
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
    print_time_diff(sigmoid_start, time.time())

    # write out any plots after sigmoid correction
    print("Plot data after correction")
    plot_corrected_team_metrics()
    
    ### combine metrics to overall score and plot ###
    # nothing needed for clutch rating here
    # Defensive Rating
    defensive_rating_combine_metrics([defensive_rating_get_shots_against_dict(),
        defensive_rating_get_goals_against_dict(),
        defensive_rating_get_pk_dict()])
    write_out_file("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], defensive_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/defensive_rating_final.png")))

    # Offensive Rating
    offensive_rating_combine_metrics([offensive_rating_get_shots_for_dict(),
        offensive_rating_get_goals_for_dict(), offensive_rating_get_pp_dict()])
    write_out_file("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], offensive_rating_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/offensive_rating_final.png")))

    # Recent Form
    recent_form_combine_metrics()
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], recent_form_get_dict())
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_final.png")))

    # combine all factors and plot the total rankings
    print("Combining All Metrics")
    combine_all_team_factors(UPDATE_TRENDS)

    ### Update any trend files if set ###
    if UPDATE_TRENDS:
        print("Updating Trend Files")

        # clutch
        update_trend_file("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
            clutch_rating_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
            ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Clutch_Rating/clutch_rating_trend.png")))

        # defensive rating
        update_trend_file("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
            defensive_rating_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
            ["Rating Date", "Defensive Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Defensive_Rating/defensive_rating_trend.png")))

        # offensive rating
        update_trend_file("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
            offensive_rating_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
            ["Rating Date", "Offensive Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Offensive_Rating/offensive_rating_trend.png")))

        # recent form
        update_trend_file("Output_Files/Team_Files/Trend_Files/RecentForm.csv",
            recent_form_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/RecentForm.csv",
            ["Rating Date", "Recent Form"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Recent_Form/recent_form_trend.png")))

        # strenght of schedule
        update_trend_file("Output_Files/Team_Files/Trend_Files/StrengthOfSchedule.csv",
            strength_of_schedule_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/StrengthOfSchedule.csv",
            ["Rating Date", "Strength of Schedule"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Strength_of_Schedule/strength_of_schedule_trend.png")))

        # absolute ranking
        absolute_rankings_update(total_rating)
        update_trend_file(
            "Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
            absolute_rankings_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
            ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
            "Graphs/Teams/Final_Rating_Score/absolute_ranking_trend.png")))

        # average ranking
        average_rankings_update(total_rating, absolute_rankings_get_dict())
        update_trend_file(
            "Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
            average_rankings_get_dict())
        plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
            ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
            "Graphs/Teams/Final_Rating_Score/average_ranking_trend.png")))

    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(subprocess_count):
        plotting_queue.put('STOP')
    for process in plotting_process_list:
        process.join()

    # remove all the instance files
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Team_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Team_Files\Instance_Files\\" + file)
            

def run_player_engine() -> None:
    # create a few match parsing processes to speed things up a bit
    subprocess_count = 15
    metric_process_list = []
    for i in range(subprocess_count):
        metric_process_list.append(Process(target=worker_node,
            args=(match_input_queue, match_output_queue,
                i)))
    for process in metric_process_list:
        process.start()

    # feed in matches until all completed matches this season have been put into
    # a process to be parsed
    match_parsing_start = time.time()
    print("Feeding in matches to workers")
    run_player_match_parser()
    
    # let the metric workers know there are no more matches
    for i in range(subprocess_count):
        match_input_queue.put('STOP')
    
    # keep reading the metric output queue until all data is returned
    print("Combining jobs from worker nodes")
    for i in range(subprocess_count):
        for output_list in iter(match_output_queue.get, 'STOP'):

            # Goalies
            goalie_metrics = output_list[0]
            goalie_utilization = goalie_metrics[0]  
            goalie_utilization_add_match_data(goalie_utilization)  
            goalie_goals_against = goalie_metrics[1]
            goalie_goals_against_add_match_data(goalie_goals_against)  
            goalie_save_percentage = goalie_metrics[2]
            goalie_save_percentage_add_match_data(goalie_save_percentage)
            goalie_save_consistency = goalie_metrics[3]
            goalie_save_consistency_add_match_data(goalie_save_consistency)
            for goalie in goalie_utilization.keys():
                goalie_teams[goalie] = goalie_utilization[goalie][0]

            # Forwards
            forward_metrics = output_list[1]
            forward_utilization = forward_metrics[0]
            forward_utilization_add_match_data(forward_utilization)
            forward_blocks = forward_metrics[1]
            forward_blocks_add_match_data(forward_blocks)
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
            forward_contributing_games_add_match_data(forward_contribution)
            forward_multipoint = forward_metrics[8]
            forward_multipoint_games_add_match_data(forward_multipoint)
            for forward in forward_utilization[0].keys():
                forward_teams[forward] = forward_utilization[0][forward]

            # Defensemen
            defensemen_metrics = output_list[2]
            defensemen_utilization = defensemen_metrics[0]
            defensemen_utilization_add_match_data(defensemen_utilization)
            defensemen_blocks = defensemen_metrics[1]
            defensemen_blocks_add_match_data(defensemen_blocks)
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
                defensemen_teams[defensemen] = defensemen_utilization[0][
                    defensemen]

    # clean up any stats after aggregation
    ### Goalies ###
    goalie_utilization_scale_by_game(
        strength_of_schedule_get_games_played_dict(), goalie_teams)
    
    # Apply utilization correction premptively for other stats to use
    apply_sigmoid_correction(goalie_utilization_get_dict())
    goalie_goals_against_scale_by_utilization(goalie_utilization_get_dict())
    goalie_save_percentage_calculate_all()
    goalie_save_percentage_combine_metrics(
        strength_of_schedule_get_games_played_dict(),
        offensive_rating_get_pp_oppertunities_dict(),
        defensive_rating_get_pk_oppertunities_dict(),
        goalie_utilization_get_dict(), goalie_teams)
    goalie_save_consistency_scale_by_games(
        strength_of_schedule_get_games_played_dict(), goalie_teams)
    
    ### Forwards ###
    forward_utilization_scale_all(
        strength_of_schedule_get_games_played_dict(),
        offensive_rating_get_pp_oppertunities_dict(),
        defensive_rating_get_pk_oppertunities_dict(), forward_teams)
    forward_utilization_combine_metrics([
        forward_utilization_get_even_time_dict(),
        forward_utilization_get_pp_time_dict(),
        forward_utilization_get_pk_time_dict()])
    
    # Apply utilization correction premptively for other stats to use
    apply_sigmoid_correction(forward_utilization_get_dict())
    forward_blocks_scale_by_shots_against(
        defensive_rating_get_unscaled_shots_against_dict(), forward_teams)
    forward_contributing_games_scale_by_games(
        strength_of_schedule_get_games_played_dict(), forward_teams)
    forward_discipline_scale_by_utilization(forward_utilization_get_dict())
    forward_hits_scale_by_games(strength_of_schedule_get_games_played_dict(),
        forward_teams)
    forward_multipoint_games_scale_by_games(
        strength_of_schedule_get_games_played_dict(), forward_teams)
    forward_plus_minus_scale_by_utilization(
        forward_utilization_get_dict())
    forward_points_scale_by_games(
        strength_of_schedule_get_games_played_dict(), forward_teams)
    forward_takeaways_scale_by_utilization(forward_utilization_get_dict())
    
    ### Defensemen ###
    defensemen_utilization_scale_all(
        strength_of_schedule_get_games_played_dict(),
        offensive_rating_get_pp_oppertunities_dict(),
        defensive_rating_get_pk_oppertunities_dict(), defensemen_teams)
    defensemen_utilization_combine_metrics([
        defensemen_utilization_get_even_time_dict(),
        defensemen_utilization_get_pp_time_dict(),
        defensemen_utilization_get_pk_time_dict()])
    
    # Apply utilization correction premptively for other stats to use
    apply_sigmoid_correction(defensemen_utilization_get_dict())
    defensemen_blocks_scale_by_shots_against(
        defensive_rating_get_unscaled_shots_against_dict(), defensemen_teams)
    defensemen_discipline_scale_by_utilization(
        defensemen_utilization_get_dict())
    defensemen_hits_scale_by_games(strength_of_schedule_get_games_played_dict(),
        defensemen_teams)
    defensemen_plus_minus_scale_by_utilization(
        defensemen_utilization_get_dict())
    defensemen_points_scale_by_games(
        strength_of_schedule_get_games_played_dict(), defensemen_teams)
    defensemen_takeaways_scale_by_utilization(defensemen_utilization_get_dict())
    print_time_diff(match_parsing_start, time.time())
    
    # now start the processes for plotting
    plotting_process_list = []
    for i in range(int(subprocess_count/2)):
        plotting_process_list.append(Process(target=worker_node,
            args=(plotting_queue, dummy_queue, i)))
    for process in plotting_process_list:
        process.start()
    
    # write out any plots before sigmoid correction
    print("Plot data before correction")
    plot_uncorrected_player_metrics()

    ### apply all sigmoid corrections ###
    print("Apply corrections")
    sigmoid_start = time.time()

    # Goalies
    apply_sigmoid_correction(goalie_goals_against_get_dict(), True)
    apply_sigmoid_correction(goalie_save_percentage_get_dict())
    apply_sigmoid_correction(goalie_save_consistency_get_dict())

    # Forwards
    apply_sigmoid_correction(forward_blocks_get_dict())
    apply_sigmoid_correction(forward_discipline_get_dict(), True)
    apply_sigmoid_correction(forward_hits_get_dict())
    apply_sigmoid_correction(forward_plus_minus_get_dict())
    apply_sigmoid_correction(forward_points_get_dict())
    apply_sigmoid_correction(forward_takeaways_get_dict())
    apply_sigmoid_correction(forward_contributing_games_get_dict())
    apply_sigmoid_correction(forward_multipoint_games_get_dict())

    # Defensemen
    apply_sigmoid_correction(defensemen_blocks_get_dict())
    apply_sigmoid_correction(defensemen_discipline_get_dict(), True)
    apply_sigmoid_correction(defensemen_hits_get_dict())
    apply_sigmoid_correction(defensemen_plus_minus_get_dict())
    apply_sigmoid_correction(defensemen_points_get_dict())
    apply_sigmoid_correction(defensemen_takeaways_get_dict())
    print_time_diff(sigmoid_start, time.time())

    # write out any plots after sigmoid correction #
    print("Plot data after correction")
    plot_corrected_player_metrics()

    ### combine metrics to overall score and plot ###
    print("Combining All Metrics")

    # Goalies
    print("\tCombining Goalie Metrics")
    goalie_total_rating = {}
    for goalie in goalie_utilization_get_dict().keys():
        goalie_total_rating[goalie] = \
            (goalie_utilization_get_dict()[goalie] *
                goalie_rating_weights.UTILIZATION_WEIGHT.value) + \
            (goalie_save_percentage_get_dict()[goalie] *
                goalie_rating_weights.SAVE_PERCENTAGE_WEIGHT.value) + \
            (goalie_goals_against_get_dict()[goalie] *
                goalie_rating_weights.GOALS_AGAINST_WEIGHT.value) + \
            (goalie_save_consistency_get_dict()[goalie] *
                goalie_rating_weights.SAVE_CONSISTENCY_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Goalie_Files/Instance_Files/Goalie_Total_Rating.csv",
        ["Goalie", "Total Rating", "Team"], goalie_total_rating, goalie_teams)
    plot_player_ranking(
        "Output_Files/Goalie_Files/Instance_Files/Goalie_Total_Rating.csv",
        ["Goalie", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Goalies/Goalie_Total_Rating/goalie_total_rating.png")
    
    # Forwards
    print("\tCombining Forward Metrics")
    forward_total_rating = {}
    for forward in forward_utilization_get_dict().keys():
        forward_total_rating[forward] = \
            (forward_hits_get_dict()[forward] *
                forward_rating_weights.HITS_WEIGHT.value) + \
            (forward_blocks_get_dict()[forward] *
                forward_rating_weights.SHOT_BLOCKING_WEIGHT.value) + \
            (forward_utilization_get_dict()[forward] *
                forward_rating_weights.UTILIZATION_WEIGHT.value) + \
            (forward_discipline_get_dict()[forward] *
                forward_rating_weights.DISIPLINE_WEIGHT.value) + \
            (forward_plus_minus_get_dict()[forward] *
                forward_rating_weights.PLUS_MINUS_WEIGHT.value) + \
            (forward_points_get_dict()[forward] *
                forward_rating_weights.POINTS_WEIGHT.value) + \
            (forward_takeaways_get_dict()[forward] * \
                forward_rating_weights.TAKEAWAYS_WEIGHT.value) + \
            (forward_contributing_games_get_dict()[forward] *
                forward_rating_weights.CONTRIBUTION_WEIGHT.value) + \
            (forward_multipoint_games_get_dict()[forward] *
                forward_rating_weights.MULTIPOINT_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Forward_Files/Instance_Files/" + \
            "Forward_Total_Rating.csv",
        ["Forward", "Total Rating", "Team"], forward_total_rating,
        forward_teams)
    plot_player_ranking(
        "Output_Files/Forward_Files/Instance_Files/" + \
            "Forward_Total_Rating.csv",
        ["Forward", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Forward/Forward_Total_Rating/forward_total_rating.png")

    # Defense
    print("\tCombining Defensemen Metrics")
    defensemen_total_rating = {}
    for defensemen in defensemen_utilization_get_dict().keys():
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
                defensemen_rating_weights.POINTS_WEIGHT.value) + \
            (defensemen_takeaways_get_dict()[defensemen] * \
                defensemen_rating_weights.TAKEAWAYS_WEIGHT.value)
    write_out_player_file(
        "Output_Files/Defensemen_Files/Instance_Files/" + \
            "Defensemen_Total_Rating.csv",
        ["Defensemen", "Total Rating", "Team"], defensemen_total_rating,
        defensemen_teams)
    plot_player_ranking(
        "Output_Files/Defensemen_Files/Instance_Files/" + \
            "Defensemen_Total_Rating.csv",
        ["Defensemen", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensemen/Defensemen_Total_Rating/defensemen_total_rating.png")
    
    # sort players into team rosters
    ### Goalies ###
    i = 1
    sorted_goalies = \
        dict(sorted(goalie_total_rating.items(), key=lambda item: item[1],
            reverse=True))
    for goalie in sorted_goalies:

        # only account for top 3 starters
        if goalie_teams[goalie] in average_goalie_rating.keys():
            if average_goalie_rating[goalie_teams[goalie]][1] < 4:
                average_goalie_rating[goalie_teams[goalie]][0] += i
                average_goalie_rating[goalie_teams[goalie]][1] += 1
        else:
            average_goalie_rating[goalie_teams[goalie]] = [i, 1]
        i += 1
    for team in average_goalie_rating:
        if team in average_player_rating.keys():
            average_player_rating[team][0] += average_goalie_rating[team][0]
            average_player_rating[team][1] += average_goalie_rating[team][1]
        else:
            average_player_rating[team] = [average_goalie_rating[team][0],
                average_goalie_rating[team][1]]
        average_goalie_rating[team] = \
            average_goalie_rating[team][0] / average_goalie_rating[team][1]
    write_out_file("Output_Files/Team_Files/Instance_Files/AvgGoalie.csv",
        ["Team", "Average Goalie"], average_goalie_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/AvgGoalie.csv",
        ["Team", "Average Goalie"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/average_goalie_rating.png", True)))
    
    ### Forwards ###
    i = 1
    sorted_forward = \
        dict(sorted(forward_total_rating.items(), key=lambda item: item[1],
            reverse=True))
    for forward in sorted_forward:

        # only account for top 12 starters
        if forward_teams[forward] in average_forward_rating.keys():
            if average_forward_rating[forward_teams[forward]][1] < 13:
                average_forward_rating[forward_teams[forward]][0] += i
                average_forward_rating[forward_teams[forward]][1] += 1
        else:
            average_forward_rating[forward_teams[forward]] = [i, 1]
        i += 1
    for team in average_forward_rating:
        average_player_rating[team][0] += average_forward_rating[team][0]
        average_player_rating[team][1] += average_forward_rating[team][1]
        average_forward_rating[team] = \
            average_forward_rating[team][0] / average_forward_rating[team][1]
    write_out_file("Output_Files/Team_Files/Instance_Files/AvgForward.csv",
        ["Team", "Average Forward"], average_forward_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/AvgForward.csv",
        ["Team", "Average Forward"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/average_forward_rating.png",
        True)))
    
    ### Defensemen ###
    i = 1
    sorted_defenseman = \
        dict(sorted(defensemen_total_rating.items(), key=lambda item: item[1],
            reverse=True))
    for defenseman in sorted_defenseman:

        # only account for top 6 starters
        if defensemen_teams[defenseman] in average_defenseman_rating.keys():
            if average_defenseman_rating[defensemen_teams[defenseman]][1] < 7:
                average_defenseman_rating[defensemen_teams[defenseman]][0] += i
                average_defenseman_rating[defensemen_teams[defenseman]][1] += 1
        else:
            average_defenseman_rating[defensemen_teams[defenseman]] = [i, 1]
        i += 1
    for team in average_defenseman_rating:
        average_player_rating[team][0] += average_defenseman_rating[team][0]
        average_player_rating[team][1] += average_defenseman_rating[team][1]
        average_defenseman_rating[team] = \
            average_defenseman_rating[team][0] / \
                average_defenseman_rating[team][1]
    write_out_file("Output_Files/Team_Files/Instance_Files/AvgDefenseman.csv",
        ["Team", "Average Defenseman"], average_defenseman_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/AvgDefenseman.csv",
        ["Team", "Average Defenseman"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/average_defenseman_rating.png",
        True)))
    
    ### All Roles ###
    for team in average_player_rating:
        average_player_rating[team] = average_player_rating[team][0] / \
            average_player_rating[team][1]
    write_out_file("Output_Files/Team_Files/Instance_Files/AvgPlayer.csv",
        ["Team", "Average Player"], average_player_rating)
    plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/AvgPlayer.csv",
        ["Team", "Average Player"], 0.0, 0.0, [],
        "Graphs/Teams/Average_Player_Ratings/average_player_rating.png",
        True)))


    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(int(subprocess_count/2)):
        plotting_queue.put('STOP')
    for process in plotting_process_list:
        while process.is_alive():
            pass

    # remove all the instance files
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
        os.walk(os.getcwd() + "\Output_Files\Defensemen_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Defensemen_Files\Instance_Files\\" + file)


if __name__ == "__main__":

    UPDATE_TRENDS = False
    REG_SEASON_COMPLETE = False
    start = time.time()
    freeze_support()

    # regardless of command parse the input files
    parse_start = time.time()
    print("Parsing All Data Files:")
    parse_all_data_files()
    print_time_diff(parse_start, time.time())
    
    # get all the match data
    match_data_start = time.time()
    print("Gathering All Match Data")
    get_game_records()
    print_time_diff(match_data_start, time.time())

    # first run the team engine which calculates and plots all team stats
    print("Running Team Engine")
    run_team_engine()
    
    # now run the player engine
    print("Running Player Engine")
    run_player_engine()
    print(time.time() - start)
    exit(0)
