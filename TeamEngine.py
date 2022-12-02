from multiprocessing import Process, Queue, freeze_support
import os
import time

# import all custom modules for parsing
from Team_Metrics.Average_Ranking_Parser import average_rankings_get_dict, \
    average_rankings_parse, average_ranking_get_ranking_dates, \
    average_rankings_update
from Team_Metrics.Absolute_Ranking_Parser import absolute_rankings_get_dict, \
    absolute_rankings_parse, absolute_rankings_update
from CSV_Writer import write_out_file, update_trend_file
from Worker_Nodes import plotter_worker

# import all custom modules for statistical analysis
from Team_Metrics.Strength_of_Schedule import strength_of_schedule_get_dict, \
    strength_of_schedule_calculate
from Team_Metrics.Win_Rating import win_rating_get_dict, win_rating_calc
from Team_Metrics.Offensive_Rating import offensive_rating_get_data_set, \
    offensive_rating_get_dict, offensive_rating_combine_metrics
from Team_Metrics.Defensive_Rating import defensive_rating_get_data_set, \
    defensive_rating_get_dict, defensive_rating_combine_metrics
from Team_Metrics.Clutch import clutch_rating_get_dict, \
    clutch_calculate_lead_protection
from Team_Metrics.Recent_Form import recent_form_get_dict, \
    recent_form_calculate_rating
from Sigmoid_Correction import apply_sigmoid_correction
from Weights import total_rating_weights
from Plotter import plot_data_set, plot_trend_set


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


'''
Combined specialized parser to get cumulative data needed all ranking factors
'''
def parse_all_data_files() -> None:
    average_rankings_parse('Output_Files/Trend_Files/AverageRankings.csv')
    absolute_rankings_parse('Output_Files/Trend_Files/AbsoluteRankings.csv')


'''
Helper functions that calculate the various factors used to create the final
    ranking score
'''
def calculate_strenght_of_schedule(update_trends : bool=True) -> None:

    # scale the strength of schedule by game, write out again, and graph
    strength_of_schedule_calculate(average_rankings_get_dict(),
        average_ranking_get_ranking_dates())
    write_out_file("Output_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"], strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/StengthOfScheduleBase.csv",
        ["Team", "Strength of Schedule Base"],
        max(list(strength_of_schedule_get_dict().values())),
        min(list(strength_of_schedule_get_dict().values())), [],
        "Graphs/Strength_of_Schedule/sos_game_scale.png")))

    # apply sigmoid correction, write out again, and graph
    apply_sigmoid_correction(strength_of_schedule_get_dict())
    write_out_file("Output_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"],
        strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/StengthOfScheduleCorrected.csv",
        ["Team", "Strength of Schedule Corrected"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Strength_of_Schedule/strenght_of_schedule_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/StrengthOfSchedule.csv",
            strength_of_schedule_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/StrengthOfSchedule.csv",
        ["Rating Date", "Strength of Schedule"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Strength_of_Schedule/strength_of_schedule_trend.png")))


def calculate_win_rating(update_trends : bool=True) -> None:

    # calculate the win rating and graph
    win_rating_calc()
    write_out_file("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating Base"], win_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating Base"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Win_Rating/win_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/WinRating.csv",
            win_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/WinRating.csv",
        ["Rating Date", "Win Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Win_Rating/win_rating_trend.png")))


def calculate_clutch_rating(update_trends : bool=True) -> None:

    # first calculate the positive part of the clutch rating
    clutch_calculate_lead_protection()

    # finally combine the factors, write out, and plot
    apply_sigmoid_correction(clutch_rating_get_dict())
    write_out_file("Output_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating Base"], clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating Base"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Clutch_Rating/clutch_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/ClutchRating.csv",
            clutch_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/ClutchRating.csv",
        ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Clutch_Rating/clutch_rating_trend.png")))


def calculate_offensive_rating(update_trends : bool=True) -> None:
    offensive_metrics = offensive_rating_get_data_set()

    # plot each metric before sigmoid
    write_out_file("Output_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"], offensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/ShotsForRatingBase.csv",
        ["Team", "Shots For Base"],
        max(list(offensive_metrics[0].values())),
        min(list(offensive_metrics[0].values())), [],
        "Graphs/offensive_Rating/shots_for_per_game_base.png")))
    write_out_file("Output_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"], offensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/GoalsForRatingBase.csv",
        ["Team", "Goals For Base"],
        max(list(offensive_metrics[1].values())),
        min(list(offensive_metrics[1].values())), [],
        "Graphs/offensive_Rating/goals_for_per_game_base.png")))
    write_out_file("Output_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], offensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/PPRatingBase.csv",
        ["Team", "Power Play Base"], max(list(offensive_metrics[2].values())),
        min(list(offensive_metrics[2].values())), [],
        "Graphs/offensive_Rating/power_play_base.png")))
    
    # apply sigmoid corrections
    for metric_dict in offensive_metrics:
        apply_sigmoid_correction(metric_dict)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"], offensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/ShotsForRatingCorr.csv",
        ["Team", "Shots For Corrected"],
        max(list(offensive_metrics[0].values())),
        min(list(offensive_metrics[0].values())), sigmoid_ticks,
        "Graphs/offensive_Rating/shots_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"], offensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/GoalsForRatingCorr.csv",
        ["Team", "Goals For Corrected"],
        max(list(offensive_metrics[1].values())),
        min(list(offensive_metrics[1].values())), sigmoid_ticks,
        "Graphs/offensive_Rating/goals_for_per_game_sigmoid.png")))
    write_out_file("Output_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"], offensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/PPRatingCorr.csv",
        ["Team", "Power Play Corrected"],
        max(list(offensive_metrics[2].values())),
        min(list(offensive_metrics[2].values())), sigmoid_ticks,
        "Graphs/offensive_Rating/power_play_sigmoid.png")))

    # combine metrics to overall score and plot
    offensive_rating_combine_metrics(offensive_metrics)
    write_out_file("Output_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/OffensiveRating.csv",
        ["Team", "Offensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/offensive_Rating/offensive_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/OffensiveRating.csv",
            offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/OffensiveRating.csv",
        ["Rating Date", "Offensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Offensive_Rating/offensive_rating_trend.png")))


def calculate_defensive_rating(update_trends : bool=True) -> None:
    defensive_metrics = defensive_rating_get_data_set()

    # plot each metric before sigmoid
    write_out_file("Output_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"], defensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/ShotsAgaRatingBase.csv",
        ["Team", "Shots Against Base"],
        min(list(defensive_metrics[0].values())),
        max(list(defensive_metrics[0].values())), [],
        "Graphs/Defensive_Rating/shots_against_per_game_base.png", True)))
    write_out_file("Output_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"], defensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/GoalsAgaRatingBase.csv",
        ["Team", "Goals Against Base"],
        min(list(defensive_metrics[1].values())),
        max(list(defensive_metrics[1].values())), [],
        "Graphs/Defensive_Rating/goals_against_per_game_base.png", True)))
    write_out_file("Output_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"], defensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/PKRatingBase.csv",
        ["Team", "Penalty Kill Base"],
        max(list(defensive_metrics[2].values())),
        min(list(defensive_metrics[2].values())), [],
        "Graphs/Defensive_Rating/penalty_kill_base.png")))
    
    # apply sigmoid corrections
    apply_sigmoid_correction(defensive_metrics[0], True)
    apply_sigmoid_correction(defensive_metrics[1], True)
    apply_sigmoid_correction(defensive_metrics[2], False)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"], defensive_metrics[0])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/ShotsAgaRatingCorr.csv",
        ["Team", "Shots Against Corrected"],
        max(list(defensive_metrics[0].values())),
        min(list(defensive_metrics[0].values())), sigmoid_ticks,
        "Graphs/Defensive_Rating/shots_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"], defensive_metrics[1])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/GoalsAgaRatingCorr.csv",
        ["Team", "Goals Against Corrected"],
        max(list(defensive_metrics[1].values())),
        min(list(defensive_metrics[1].values())), sigmoid_ticks,
        "Graphs/Defensive_Rating/goals_against_per_game_sigmoid.png")))
    write_out_file("Output_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"], defensive_metrics[2])
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/PKRatingCorr.csv",
        ["Team", "Penalty Kill Corrected"],
        max(list(defensive_metrics[2].values())),
        min(list(defensive_metrics[2].values())), sigmoid_ticks,
        "Graphs/Defensive_Rating/penalty_kill_sigmoid.png")))

    # combine metrics to overall score and plot
    defensive_rating_combine_metrics(defensive_metrics)
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], defensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating Final"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Defensive_Rating/defensive_rating_final.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/DefensiveRating.csv",
            offensive_rating_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/DefensiveRating.csv",
        ["Rating Date", "Defensive Rating"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Defensive_Rating/defensive_rating_trend.png")))


def calculate_recent_form(update_trends : bool=True) -> None:
    
    # first calculate the recent form raw rating and plot
    recent_form_calculate_rating()
    write_out_file("Output_Files/Instance_Files/RecentFormBase.csv",
        ["Team", "Recent Form"], recent_form_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/RecentFormBase.csv",
        ["Team", "Recent Form"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Recent_Form/recent_form_base.png")))

    # now apply the sigmoid correction and plot
    apply_sigmoid_correction(recent_form_get_dict())
    write_out_file("Output_Files/Instance_Files/RecentFormCorr.csv",
        ["Team", "Recent Form"], recent_form_get_dict())
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/RecentFormCorr.csv",
        ["Team", "Recent Form"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Recent_Form/recent_form_final.png")))

    # update the trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/RecentForm.csv",
            recent_form_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/RecentForm.csv",
        ["Rating Date", "Recent Form"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Recent_Form/recent_form_trend.png")))


'''
Function to create the combined set of all metrics into one ranking score
'''
def combine_all_factors(update_trends : bool=True) -> None:
    
    # calculate the final rating for all teams using the forms above
    for team in total_rating.keys():
        total_rating[team] = \
            (win_rating_get_dict()[team] * \
                total_rating_weights.WIN_RATING_WEIGHT.value) + \
            (clutch_rating_get_dict()[team] * \
                total_rating_weights.CLUTCH_RATING_WEIGHT.value) + \
            (recent_form_get_dict()[team] * \
                total_rating_weights.FORM_RATING_WEIGHT.value) + \
            (strength_of_schedule_get_dict()[team] * \
                total_rating_weights.SOS_RATING_WEIGHT.value) + \
            (offensive_rating_get_dict()[team] * \
                total_rating_weights.OFFENSIVE_RATING_WEIGHT.value) + \
            (defensive_rating_get_dict()[team] * \
                total_rating_weights.DEFENSIVE_RATING_WEIGHT.value)

    # write out and plot the total ratings
    write_out_file("Output_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], total_rating)
    team_engine_plotting_queue.put((plot_data_set,
        ("Output_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], 1.0, 0.0, sigmoid_ticks,
        "Graphs/Final_Rating_Score/final_rating_score.png")))

    # update trend file
    if update_trends:
        update_trend_file("Output_Files/Trend_Files/RatingScore.csv",
            total_rating)
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/RatingScore.csv",
        ["Rating Date", "Rating Score"], 1.1, -.1, sigmoid_ticks,
        "Graphs/Final_Rating_Score/rating_score_trend.png")))


def update_absolute_rankings() -> None:
    absolute_rankings_update(total_rating)
    update_trend_file("Output_Files/Trend_Files/AbsoluteRankings.csv",
        absolute_rankings_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/AbsoluteRankings.csv",
        ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Final_Rating_Score/absolute_ranking_trend.png")))


def update_average_rankings() -> None:
    average_rankings_update(total_rating, absolute_rankings_get_dict())
    update_trend_file("Output_Files/Trend_Files/AverageRankings.csv",
        average_rankings_get_dict())
    team_engine_plotting_queue.put((plot_trend_set,
        ("Output_Files/Trend_Files/AverageRankings.csv",
        ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
        "Graphs/Final_Rating_Score/average_ranking_trend.png")))


if __name__ == "__main__":

    UPDATE_TRENDS = False

    # set up multiprocess to be ready in case a subprocess freezes
    freeze_support()
    start = time.time()

    # create a few plotting processes to speed things up a bit
    subprocess_count = 3
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
    print("Recent Form")
    calculate_recent_form(UPDATE_TRENDS)

    print("Strenght of Schedule")
    calculate_strenght_of_schedule(UPDATE_TRENDS)

    print("Win Rating")
    calculate_win_rating(UPDATE_TRENDS)

    print("Clutch Rating")
    calculate_clutch_rating(UPDATE_TRENDS)

    print("Offensive Rating")
    calculate_offensive_rating(UPDATE_TRENDS)

    print("Defensive Rating")
    calculate_defensive_rating(UPDATE_TRENDS)

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

    # stop all the running workers
    for i in range(subprocess_count):
        team_engine_plotting_queue.put('STOP')

    for process in process_list:
        while process.is_alive():
            pass

    # remove all the instance files
    for dir in \
        os.walk(os.getcwd() + "\Output_Files\Instance_Files"):
        for file in dir[2]:
            os.remove(os.getcwd() +
                "\Output_Files\Instance_Files\\" + file)

    print(time.time() - start)
