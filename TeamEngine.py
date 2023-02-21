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
    clutch_rating_get_trend_dict, clutch_calculate_lead_protection
from Team_Metrics.Defensive_Rating import defensive_rating_get_dict, \
    defensive_rating_get_trend_dict
from Team_Metrics.Offensive_Rating import offensive_rating_get_dict, \
    offensive_rating_get_trend_dict
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_get_trend_dict
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


class Metric_Order(Enum):
    CLUTCH = 0
    DEFENSIVE = 1
    OFFENSIVE = 2
    RECENT = 3
    SOS = 4


'''
Combined specialized parser to get cumulative data needed all ranking factors
'''
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


'''
Pull all game records from the API database
'''
def get_game_records() -> None:
    records_url = \
        "https://statsapi.web.nhl.com/api/v1/schedule?season=20222023" + \
            "&gameType=R&expand=schedule.linescore"
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    # matches are orginized by date they take place
    for date in parsed_data["dates"]:
        game_data = []

        # for each game on a specific date loop through
        for game in date["games"]:

            # if the game is a completed regular season game then add to list
            if (game["status"]["abstractGameState"] == "Final"):
                game_data.append(game)
        
        # now update the current date with all games from that day we just
        # finished collecting
        season_matches[date["date"]] = game_data

'''
Worker node for running multiprocess calls
'''
def worker_node(input_queue : Queue=None, output_queue : Queue=None,
                id : int=0) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    print("Exiting! Worker {} ran {} jobs".format(id, i))
    output_queue.put('STOP')


'''
Parse a single match getting all of the data for every metric and updating
the total value based on that.
'''
def parse_match(match_data : dict={}, relative_metrics : list=[]) -> list:
    metric_data = []

    # get home and away team
    home_team = match_data["teams"]["home"]["team"]["name"]
    away_team = match_data["teams"]["away"]["team"]["name"]

    # clutch rating
    clutch_data = clutch_calculate_lead_protection(match_data)
    clutch_data[0][home_team] *= relative_metrics[Metric_Order.CLUTCH.value][0]
    clutch_data[1][away_team] *= relative_metrics[Metric_Order.CLUTCH.value][1]
    metric_data.append(clutch_data)

    # return the list of all metric data for this match
    return metric_data


'''
Function to create the combined set of all metrics into one ranking score
'''
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


def update_absolute_rankings() -> None:
    absolute_rankings_update(total_rating)
    update_trend_file("Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
        absolute_rankings_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv",
        ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Teams/Final_Rating_Score/absolute_ranking_trend.png")))


def update_average_rankings() -> None:
    average_rankings_update(total_rating, absolute_rankings_get_dict())
    update_trend_file("Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
        average_rankings_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/AverageRankings.csv",
        ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Teams/Final_Rating_Score/average_ranking_trend.png")))


if __name__ == "__main__":

    UPDATE_TRENDS = False
    start = time.time()
    freeze_support()

    # regardless of command parse the input files
    print("Parsing All Data Files")
    parse_all_data_files()
    
    print("Gathering All Match Data")
    get_game_records()

    # get all the different parsed trend data dictionaries
    clutch_trends = clutch_rating_get_trend_dict()
    defensive_trends = defensive_rating_get_trend_dict()
    offensive_trends = offensive_rating_get_trend_dict()
    recent_form_trends = recent_form_get_trend_dict()
    sos_trends = strength_of_schedule_get_trend_dict()

    # create a few match parsing processes to speed things up a bit
    subprocess_count = 15
    process_list = []
    for i in range(subprocess_count):
        process_list.append(Process(target=worker_node,
            args=(team_engine_match_input_queue, team_engine_match_output_queue,
                i)))
    for process in process_list:
        process.start()

    # feed in matches until all completed matches this season have been put into
    # a process to be parsed
    date_count = 0
    final_period = False
    current_rating_period = average_ranking_get_ranking_dates()[date_count]
    next_rating_period = average_ranking_get_ranking_dates()[date_count + 1]
    for date in season_matches:
        parsed_date = date.split("-")
        parsed_date = datetime.date(int(parsed_date[0]), int(parsed_date[1]),
            int(parsed_date[2]))
        for match in season_matches[date]:
            
            # get the home and away team
            away_team = match["teams"]["away"]["team"]["name"]
            home_team = match["teams"]["home"]["team"]["name"]
            if parsed_date < current_rating_period:
                clutch_stats = [1.0,1.0]
                defensive_stats = [1.0,1.0]
                offensive_stats = [1.0,1.0]
                recent_form_stats = [1.0,1.0]
                sos_stats = [1.0,1.0]
            else: 
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
                recent_form_stats = [
                    recent_form_trends[home_team][date_count],
                    recent_form_trends[away_team][date_count]
                ]
                sos_stats = [
                    sos_trends[home_team][date_count],
                    sos_trends[away_team][date_count]
                ]
            team_engine_match_input_queue.put((parse_match,
                (match, [clutch_stats, defensive_stats, offensive_stats,
                    recent_form_stats, sos_stats])))

    # let the metric workers know there are no more matches
    for i in range(subprocess_count):
        team_engine_match_input_queue.put('STOP')
    
    # keep reading the metric output queue until all data is returned
    stop_count = 0
    for i in range(subprocess_count):
        for output_list in iter(team_engine_match_output_queue.get, 'STOP'):
            clutch_return = output_list[Metric_Order.CLUTCH.value]
            clutch_rating_get_dict()[list(clutch_return[0].keys())[0]] += \
                list(clutch_return[0].values())[0]
            clutch_rating_get_dict()[list(clutch_return[1].keys())[0]] += \
                list(clutch_return[1].values())[0]

    print(clutch_rating_get_dict())
    exit(0)

    # combine all factors and plot the total rankings
    print("Combining All Metrics")
    combine_all_factors(UPDATE_TRENDS)

    # absolute rating
    if UPDATE_TRENDS:
        print("Updating Absolute Ranking")
        update_absolute_rankings()

    # average rankings
    if UPDATE_TRENDS:
        print("Updating Average Ranking")
        update_average_rankings()

    # stop all the running workers
    print("Waiting for Plotters to finish their very hard work <3")
    for i in range(subprocess_count):
        team_engine_plotting_queue.put('STOP')

    for process in process_list:
        while process.is_alive():
            pass

    # remove all the instance files
    for dir in \
        os.walk(os.getcwd() + "\Output_Files/Team_Files/\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files/Team_Files/\Instance_Files\\" + file)

    print(time.time() - start)
