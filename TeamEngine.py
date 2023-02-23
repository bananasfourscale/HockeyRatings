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

# import all custom modules for statistical analysis
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_rating_get_trend_dict, clutch_calculate_lead_protection, \
    clutch_add_match_data
from Team_Metrics.Defensive_Rating import defensive_rating_get_dict, \
    defensive_rating_get_shots_against_dict, \
    defensive_rating_get_goals_against_dict, defensive_rating_get_pk_dict, \
    defensive_rating_get_trend_dict, defensive_rating_get_data_set, \
    defensive_rating_add_match_data, defensive_rating_calculate_penalty_kill, \
    defensive_rating_combine_metrics
from Team_Metrics.Offensive_Rating import offensive_rating_get_dict, \
    offensive_rating_get_shots_for_dict, offensive_rating_get_goals_for_dict, \
    offensive_rating_get_pp_dict, offensive_rating_get_trend_dict, \
    offensive_rating_get_data_set, offensive_rating_add_match_data, \
    offensive_rating_calculate_power_play, offensive_rating_combine_metrics
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_get_streak_dict, recent_form_get_last_10_dict, \
    recent_form_get_last_20_dict, recent_form_get_last_40_dict, \
    recent_form_get_trend_dict, recent_form_get_data_set, \
    recent_form_add_match_data, recent_form_calculate_all, \
    recent_form_combine_metrics 
from Team_Metrics.Strength_of_Schedule import strength_of_schedule_get_dict, \
    strength_of_schedule_get_trend_dict

# shared engine tools
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import total_rating_weights
from Plotter import plot_data_set, plot_trend_set
from CSV_Writer import write_out_file, update_trend_file


sigmoid_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


total_rating = {
    'Anaheim Ducks' : 0,
    'Arizona Coyotes' : 0,
    'Boston Bruins' : 0,
    'Buffalo Sabres' : 0,
    'Calgary Flames' : 0,
    'Carolina Hurricanes' : 0,
    'Chicago Blackhawks' : 0,
    'Colorado Avalanche' : 0,
    'Columbus Blue Jackets' : 0,
    'Dallas Stars' : 0,
    'Detroit Red Wings' : 0,
    'Edmonton Oilers' : 0,
    'Florida Panthers' : 0,
    'Los Angeles Kings' : 0,
    'Minnesota Wild' : 0,
    'Montréal Canadiens' : 0,
    'Nashville Predators' : 0,
    'New Jersey Devils' : 0,
    'New York Islanders' : 0,
    'New York Rangers' : 0,
    'Ottawa Senators' : 0,
    'Philadelphia Flyers' : 0,
    'Pittsburgh Penguins' : 0,
    'San Jose Sharks' : 0,
    'Seattle Kraken' : 0,
    'St. Louis Blues' : 0,
    'Tampa Bay Lightning' : 0,
    'Toronto Maple Leafs' : 0,
    'Vancouver Canucks' : 0,
    'Vegas Golden Knights' : 0,
    'Washington Capitals' : 0,
    'Winnipeg Jets' : 0,
}


season_matches = {}


team_engine_match_input_queue = Queue()
team_engine_match_output_queue = Queue()
team_engine_plotting_queue = Queue()
dummy_queue = Queue()


class Metric_Order(Enum):
    CLUTCH = 0
    DEFENSIVE = 1
    OFFENSIVE = 2
    RECENT = 3
    SOS = 4


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


def print_time_diff(start_time : float=0.0, end_time : float=0.0) -> None:
    print("Completed in {} seconds".format(end_time - start_time))


def get_game_records() -> None:
    schedule = \
        "https://statsapi.web.nhl.com/api/v1/schedule?season=20222023" + \
            "&gameType=R&expand=schedule.linescore"
    schedule_web_data = requests.get(schedule)
    schedule_parsed_data = json.loads(schedule_web_data.content)

    # matches are orginized by date they take place
    for date in schedule_parsed_data["dates"]:
        game_data = []

        # for each game on a specific date loop through
        for game in date["games"]:

            # if the game is a completed regular season game then add to list
            if (game["status"]["abstractGameState"] == "Final"):
                box_score = \
                    "https://statsapi.web.nhl.com/api/v1/game/" + \
                        "{}/boxscore".format(game["gamePk"])
                box_score_web_data = requests.get(box_score)
                box_score_parsed_data = json.loads(box_score_web_data.content)
                game_data.append({'boxscore':box_score_parsed_data,
                    'linescore':game})
        
        # now update the current date with all games from that day we just
        # finished collecting
        season_matches[date["date"]] = game_data


def worker_node(input_queue : Queue=None, output_queue : Queue=None,
                id : int=0) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    print("Exiting! Worker {} ran {} jobs".format(id, i))
    output_queue.put('STOP')


def feed_parser_jobs() -> None:

    # get all the different parsed trend data dictionaries
    clutch_trends = clutch_rating_get_trend_dict()
    defensive_trends = defensive_rating_get_trend_dict()
    offensive_trends = offensive_rating_get_trend_dict()
    recent_form_trends = recent_form_get_trend_dict()
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
                clutch_stats = [1.0,1.0]
                defensive_stats = [1.0,1.0]
                offensive_stats = [1.0,1.0]
                recent_form_stats = [1.0,1.0]
                sos_stats = [1.0,1.0]

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
                clutch_stats = [
                    clutch_trends[home_team][date_count],
                    clutch_trends[away_team][date_count]
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
                # for now just give a 1.0 for every team
                recent_form_stats = [1.0,1.0]
                sos_stats = [
                    sos_trends[home_team][date_count],
                    sos_trends[away_team][date_count]
                ]

            # feed the match information with the scale factors for each team
            # into the match parser which will call all metrics to get all
            # relevant information required
            team_engine_match_input_queue.put((parse_match,
                (match, [clutch_stats, defensive_stats, offensive_stats,
                    recent_form_stats, sos_stats])))


def parse_match(match_data : dict={}, relative_metrics : list=[]) -> list:
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
    defensive_data[0][home_team] *= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[0][away_team] *= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    
    # goals against
    defensive_data[1][home_team] *= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[1][away_team] *= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.HOME.value]
    
    # penalty kill oppertunities
    defensive_data[2][home_team][0] *= \
        relative_metrics[Metric_Order.OFFENSIVE.value][
            Team_Selection.AWAY.value]
    defensive_data[2][away_team][0] *= \
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

    # return the list of all metric data for this match
    return metric_data


def plot_unscaled_metrics() -> None:

    ### Clutch Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ClutchRatingBase.csv",
        ["Team", "Clutch Rating Base"], clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ClutchRatingBase.csv",
        ["Team", "Clutch Rating Base"], 0.0, 0.0, [],
        "Graphs/Teams/Clutch_Rating/clutch_rating_base.png")))

    ### Defensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"],
        defensive_rating_get_shots_against_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"],
        defensive_rating_get_goals_against_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], defensive_rating_get_pk_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/penalty_kill_base.png")))

    ### Offensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], offensive_rating_get_shots_for_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], offensive_rating_get_goals_for_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], offensive_rating_get_pp_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/power_play_base.png")))

    ### Recent Form ###
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], recent_form_get_streak_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Average Streak Score Base"], 0.0, 0.0, [],
        "Graphs/Teams/Recent_Form/recent_form_streak_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Teams/Recent_Form/recent_form_last_ten_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast20Base.csv",
        ["Team", "Last Twenty Games"], 20.0, 0,
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "Graphs/Teams/Recent_Form/recent_form_last_twenty_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast40Base.csv",
        ["Team", "Last Fourty Games"], 40.0, 0,
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40],
        "Graphs/Teams/Recent_Form/recent_form_last_fourty_base.png")))


def plot_scaled_metrics() -> None:

    ### Clutch Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ClutchRatingFinal.csv",
        ["Team", "Clutch Rating Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/clutch_rating_final.png")))

    ### Defensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"],
        defensive_rating_get_shots_against_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"],
        defensive_rating_get_goals_against_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], defensive_rating_get_pk_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/penalty_kill_sigmoid.png")))

    ### Offensive Rating ###
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], offensive_rating_get_shots_for_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], offensive_rating_get_goals_for_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], offensive_rating_get_pp_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/power_play_sigmoid.png")))

    ### Recent Form ###
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"], recent_form_get_streak_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Average Streak Score Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_streak_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], recent_form_get_last_10_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast10Corr.csv",
        ["Team", "Last Ten Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_ten_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], recent_form_get_last_20_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast20Corr.csv",
        ["Team", "Last Twenty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_twenty_corrected.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], recent_form_get_last_40_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast40Corr.csv",
        ["Team", "Last Fourty Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_fourty_corrected.png")))


def combine_all_factors(update_trends : bool=True) -> None:
    
    # calculate the final rating for all teams using the forms above
    for team in total_rating.keys():
        total_rating[team] = \
            (clutch_rating_get_dict()[team] * \
                total_rating_weights.CLUTCH_RATING_WEIGHT.value) + \
            (defensive_rating_get_dict()[team] * \
                total_rating_weights.DEFENSIVE_RATING_WEIGHT.value) + \
            (offensive_rating_get_dict()[team] * \
                total_rating_weights.OFFENSIVE_RATING_WEIGHT.value) + \
            (recent_form_get_dict()[team] * \
                total_rating_weights.RECENT_FORM_RATING_WEIGHT.value) + \
            (strength_of_schedule_get_dict()[team] * \
                total_rating_weights.SOS_RATING_WEIGHT.value)
            

    # write out and plot the total ratings
    write_out_file("Output_Files/Team_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], total_rating)
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/final_rating_score.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/RatingScore.csv",
            total_rating)
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/RatingScore.csv",
        ["Rating Date", "Rating Score"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Final_Rating_Score/rating_score_trend.png")))


if __name__ == "__main__":

    UPDATE_TRENDS = False
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

    # create a few match parsing processes to speed things up a bit
    subprocess_count = 15
    metric_process_list = []
    for i in range(subprocess_count):
        metric_process_list.append(Process(target=worker_node,
            args=(team_engine_match_input_queue, team_engine_match_output_queue,
                i)))
    for process in metric_process_list:
        process.start()

    # feed in matches until all completed matches this season have been put into
    # a process to be parsed
    match_parsing_start = time.time()
    print("Feeding in matches to workers")
    feed_parser_jobs()
    
    # let the metric workers know there are no more matches
    for i in range(subprocess_count):
        team_engine_match_input_queue.put('STOP')
    
    # keep reading the metric output queue until all data is returned
    stop_count = 0
    print("Combining jobs from worker nodes")
    for i in range(subprocess_count):
        for output_list in iter(team_engine_match_output_queue.get, 'STOP'):

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

    # call any cleanup calculations required
    defensive_rating_calculate_penalty_kill()
    offensive_rating_calculate_power_play()
    recent_form_calculate_all()
    print_time_diff(match_parsing_start, time.time())

    # now start the processes for plotting
    plotting_process_list = []
    for i in range(subprocess_count):
        plotting_process_list.append(Process(target=worker_node,
            args=(team_engine_plotting_queue, dummy_queue, i)))
    for process in plotting_process_list:
        process.start()

    # write out any plots before sigmoid correction
    print("Plot data before correction")
    plot_unscaled_metrics()

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
    print_time_diff(sigmoid_start, time.time())

    # write out any plots after sigmoid correction
    print("Plot data after correction")
    plot_scaled_metrics()
    
    ### combine metrics to overall score and plot ###
    # nothing needed for clutch rating here
    # Defensive Rating
    defensive_rating_combine_metrics([defensive_rating_get_shots_against_dict(),
        defensive_rating_get_goals_against_dict(),
        defensive_rating_get_pk_dict()])
    write_out_file("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], defensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/defensive_rating_final.png")))

    # Offensive Rating
    offensive_rating_combine_metrics([offensive_rating_get_shots_for_dict(),
        offensive_rating_get_goals_for_dict(), offensive_rating_get_pp_dict()])
    write_out_file("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/offensive_rating_final.png")))

    # Recent Form
    recent_form_combine_metrics()
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], recent_form_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_final.png")))

    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(subprocess_count):
        team_engine_plotting_queue.put('STOP')
    for process in plotting_process_list:
        while process.is_alive():
            pass

    # combine all factors and plot the total rankings
    # print("Combining All Metrics")
    # combine_all_factors(UPDATE_TRENDS)

    if UPDATE_TRENDS:
        print("Updating Trend Files")

        # clutch
        update_trend_file("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
            clutch_rating_get_dict())
        team_engine_plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
            ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Clutch_Rating/clutch_rating_trend.png")))

        # defensive rating
        update_trend_file("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
            defensive_rating_get_dict())
        team_engine_plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
            ["Rating Date", "Defensive Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Defensive_Rating/defensive_rating_trend.png")))

        # offensive rating
        update_trend_file("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
            offensive_rating_get_dict())
        team_engine_plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
            ["Rating Date", "Offensive Rating"], 1.1, -.1, sigmoid_ticks,
            "Graphs/Teams/Offensive_Rating/offensive_rating_trend.png")))

        # absolute ranking
        absolute_rankings_update(total_rating)
        update_trend_file(
            "Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
            absolute_rankings_get_dict())
        team_engine_plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
            ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
            "Graphs/Teams/Final_Rating_Score/absolute_ranking_trend.png")))

        # average ranking
        average_rankings_update(total_rating, absolute_rankings_get_dict())
        update_trend_file(
            "Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
            average_rankings_get_dict())
        team_engine_plotting_queue.put((plot_trend_set,
            ("Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
            ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
            "Graphs/Teams/Final_Rating_Score/average_ranking_trend.png")))

    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(subprocess_count):
        team_engine_plotting_queue.put('STOP')
    for process in plotting_process_list:
        while process.is_alive():
            pass

    # remove all the instance files
    for dir in \
        os.walk(os.getcwd() + "\Output_Files/Team_Files/\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files/Team_Files/\Instance_Files\\" + file)
    print(time.time() - start)
    exit(0)
