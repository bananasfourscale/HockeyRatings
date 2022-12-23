from multiprocessing import Process, Queue, freeze_support
import requests
import json
import time
import os

# import all custom modules for parsing
from Team_Metrics.Average_Ranking_Parser import average_rankings_get_dict, \
    average_rankings_parse, average_ranking_get_ranking_dates, \
    average_rankings_update
from Team_Metrics.Absolute_Ranking_Parser import absolute_rankings_get_dict, \
    absolute_rankings_parse, absolute_rankings_update

# import all custom modules for statistical analysis
from Team_Metrics.Strength_of_Schedule import strength_of_schedule_get_dict, \
    strength_of_schedule_calculate, strength_of_schedule_scale_by_game
from Team_Metrics.Offensive_Rating import offensive_rating_get_data_set, \
    offensive_rating_get_dict, offensive_rating_combine_metrics
from Team_Metrics.Defensive_Rating import defensive_rating_get_data_set, \
    defensive_rating_get_dict, defensive_rating_combine_metrics
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_calculate_lead_protection
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_get_data_set, recent_form_calculate_last_ten, \
    recent_form_calculate_streak, recent_form_combine_metrics

# shared engine tools
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import total_rating_weights
from Plotter import plot_data_set, plot_trend_set
from CSV_Writer import write_out_file, update_trend_file
from Worker_Nodes import plotter_worker


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


team_engine_plotting_queue = Queue()


team_season_stats = {}


team_season_records = {}


season_matches = {}


'''
Combined specialized parser to get cumulative data needed all ranking factors
'''
def parse_all_data_files() -> None:
    average_rankings_parse('Output_Files/Team_Files/Trend_Files/AverageRankings.csv')
    absolute_rankings_parse('Output_Files/Team_Files/Trend_Files/AbsoluteRankings.csv')


def get_team_season_stats() -> None:

    # Team lists are so small relative to the list of all player data, just get
    # the data and store it to save time looking it up over and over
    # Get the top level record from the API
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    for team in parsed_data["teams"]:
        team_season_stats[team["name"]] = \
            team["teamStats"][0]["splits"][0]["stat"]


def get_team_season_records() -> None:
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/standings?expand=standings.record'
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)
    for record in parsed_data["records"]:
        for team in record["teamRecords"]:
            team_season_records[team["team"]["name"]] = team


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
Helper functions that calculate the various factors used to create the final
    ranking score
'''
def calculate_clutch_rating(update_trends : bool=True) -> None:

    # first calculate the positive part of the clutch rating
    clutch_calculate_lead_protection(season_matches)

    # finally combine the factors, write out, and plot
    apply_sigmoid_correction(clutch_rating_get_dict())
    write_out_file("Output_Files/Team_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating Base"], clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating Base"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/clutch_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
            clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/ClutchRating.csv",
        ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Clutch_Rating/clutch_rating_trend.png")))


def calculate_defensive_rating(update_trends : bool=True) -> None:
    defensive_metrics = defensive_rating_get_data_set(team_season_stats)

    # plot each metric before sigmoid
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], defensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], defensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_base.png", True)))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], defensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], 0.0, 0.0, [],
        "Graphs/Teams/Defensive_Rating/penalty_kill_base.png")))
    
    # apply sigmoid corrections
    apply_sigmoid_correction(defensive_metrics[0], True)
    apply_sigmoid_correction(defensive_metrics[1], True)
    apply_sigmoid_correction(defensive_metrics[2], False)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], defensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/shots_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], defensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/goals_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], defensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/penalty_kill_sigmoid.png")))

    # combine metrics to overall score and plot
    defensive_rating_combine_metrics(defensive_metrics)
    write_out_file("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], defensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/defensive_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
            offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/DefensiveRating.csv",
        ["Rating Date", "Defensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Defensive_Rating/defensive_rating_trend.png")))


def calculate_offensive_rating(update_trends : bool=True) -> None:
    offensive_metrics = offensive_rating_get_data_set(team_season_stats)

    # plot each metric before sigmoid
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], offensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], offensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_base.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], offensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], 0.0, 0.0, [],
        "Graphs/Teams/Offensive_Rating/power_play_base.png")))
    
    # apply sigmoid corrections
    for metric_dict in offensive_metrics:
        apply_sigmoid_correction(metric_dict)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], offensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/shots_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], offensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/goals_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], offensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/power_play_sigmoid.png")))

    # combine metrics to overall score and plot
    offensive_rating_combine_metrics(offensive_metrics)
    write_out_file("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/offensive_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
            offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/OffensiveRating.csv",
        ["Rating Date", "Offensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Offensive_Rating/offensive_rating_trend.png")))


def calculate_recent_form(update_trends : bool=True) -> None:
    
    # get all the data used for recent form across all metrics
    recent_form_metrics = recent_form_get_data_set(team_season_records)

    # last 10 is just a string value so actually calculate the rating and plot
    recent_form_metrics[0] = \
        recent_form_calculate_last_ten(recent_form_metrics[0])
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], recent_form_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLast10Base.csv",
        ["Team", "Last Ten Games"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Teams/Recent_Form/recent_form_last_ten_base.png")))

    recent_form_metrics[1] = \
        recent_form_calculate_streak(recent_form_metrics[1])
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Current Streak"], recent_form_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakBase.csv",
        ["Team", "Current Streak"], 0.0, 0.0, [],
        "Graphs/Teams/Recent_Form/recent_form_streak_base.png")))

    # now apply the sigmoid correction and plot
    recent_form_metrics[0] = apply_sigmoid_correction(recent_form_metrics[0])
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormLastTenCorr.csv",
        ["Team", "Last Ten Games"], recent_form_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormLastTenCorr.csv",
        ["Team", "Last Ten Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_last_ten_corrected.png")))
    recent_form_metrics[1] = apply_sigmoid_correction(recent_form_metrics[1])
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Last Ten Games"], recent_form_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormStreakCorr.csv",
        ["Team", "Last Ten Games"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_streak_corrected.png")))

    # combine the metrics and plot the final result
    recent_form_combine_metrics(recent_form_metrics)
    write_out_file("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], recent_form_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/RecentFormFinal.csv",
        ["Team", "Recent Form Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_final.png")))

    # update the trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/RecentForm.csv",
            recent_form_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/RecentForm.csv",
        ["Rating Date", "Recent Form"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Recent_Form/recent_form_trend.png")))


def calculate_strenght_of_schedule(update_trends : bool=True) -> None:

    # scale the strength of schedule by game, write out again, and graph
    strength_of_schedule_calculate(average_rankings_get_dict(),
        average_ranking_get_ranking_dates(), season_matches)
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], 0.0, 0.0, [],
        "Graphs/Teams/Strength_of_Schedule/sos_base.png")))

    strength_of_schedule_scale_by_game(team_season_stats)
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleScale.csv",
        ["Team", "Strength of Schedule Game Scale"], strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleScale.csv",
        ["Team", "Strength of Schedule Game Scale"], 0.0, 0.0, [],
        "Graphs/Teams/Strength_of_Schedule/sos_game_scale.png")))

    # apply sigmoid correction, write out again, and graph
    apply_sigmoid_correction(strength_of_schedule_get_dict())
    write_out_file("Output_Files/Team_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"],
        strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Team_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Teams/Strength_of_Schedule/strenght_of_schedule_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Team_Files/Trend_Files/StrengthOfSchedule.csv",
            strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Team_Files/Trend_Files/StrengthOfSchedule.csv",
        ["Rating Date", "Strength of Schedule"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Teams/Strength_of_Schedule/strength_of_schedule_trend.png")))


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

    # set up multiprocess to be ready in case a subprocess freezes
    freeze_support()
    start = time.time()

    print("Gathering All Team Season Stats")
    get_team_season_stats()

    print("Gathering All Team Season Records")
    get_team_season_records()

    print("Gathering All Match Data")
    get_game_records()

    # create a few plotting processes to speed things up a bit
    subprocess_count = 15
    process_list = []
    for i in range(subprocess_count):
        process_list.append(Process(target=plotter_worker,
            args=(team_engine_plotting_queue, i)))
    for process in process_list:
        process.start()

    # regardless of command parse the input files
    print("Parsing All Data Files")
    parse_all_data_files()

    # calculate all the elements of the score and plot them
    print("Strenght of Schedule")
    calculate_strenght_of_schedule(UPDATE_TRENDS)

    # print("Win Rating")
    # calculate_win_rating(UPDATE_TRENDS)

    print("Clutch Rating")
    calculate_clutch_rating(UPDATE_TRENDS)

    print("Offensive Rating")
    calculate_offensive_rating(UPDATE_TRENDS)

    print("Defensive Rating")
    calculate_defensive_rating(UPDATE_TRENDS)

    print("Recent Form")
    calculate_recent_form(UPDATE_TRENDS)

    # combine all factors and plot the total rankings
    print("Combining All Metrics")
    combine_all_factors(UPDATE_TRENDS)

    # absolute rating
    print("Updating Absolute Ranking")
    if UPDATE_TRENDS:
        update_absolute_rankings()

    # average rankings
    print("Updating Average Ranking")
    if UPDATE_TRENDS:
        update_average_rankings()
    print("Waiting for Plotters to finish their very hard work <3")

    # stop all the running workers
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
