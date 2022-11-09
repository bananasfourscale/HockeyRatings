# import all custom modules for parsing
from Team_Metrics.Average_Ranking_Parser import *
from Team_Metrics.Absolute_Ranking_Parser import *
from CSV_Writer import *

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
from Weights import *
from Plotter import plot_data_set, plot_trend_set


sigmiod_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


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

'''
Specialized plotting functions
'''


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
def calculate_strenght_of_schedule() -> None:

    # scale the strength of schedule by game, write out again, and graph
    strength_of_schedule_calculate(average_rankings_get_dict(),
        average_ranking_get_ranking_dates())
    write_out_file("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule_get_dict())
    plot_data_set("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"],
        max(list(strength_of_schedule_get_dict().values())),
        min(list(strength_of_schedule_get_dict().values())), [],
        "Graphs/Strength_of_Schedule/sos_game_scale.png")

    # apply sigmoid correction, write out again, and graph
    strength_of_schedule = apply_sigmoid_correction(
        strength_of_schedule_get_dict())
    write_out_file("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Strength_of_Schedule/strenght_of_schedule_final.png")


def calculate_win_rating() -> None:

    # calculate the win rating and graph
    win_rating_calc()
    write_out_file("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating"], win_rating_get_dict())
    plot_data_set("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Win_Rating/win_rating_final.png")


def calculate_offensive_rating() -> None:
    offensive_metrics = offensive_rating_get_data_set()

    # plot each metric before sigmoid
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Shots Against"], offensive_metrics[0])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Shots Against"], max(list(offensive_metrics[0].values())),
        min(list(offensive_metrics[0].values())), [],
        "Graphs/offensive_Rating/shots_against_per_game_base.png")
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Goals Against"], offensive_metrics[1])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Goals Against"], max(list(offensive_metrics[1].values())),
        min(list(offensive_metrics[1].values())), [],
        "Graphs/offensive_Rating/goals_against_per_game_base.png")
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Penalty Kill"], offensive_metrics[2])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Penalty Kill"], max(list(offensive_metrics[2].values())),
        min(list(offensive_metrics[2].values())), [],
        "Graphs/offensive_Rating/penalty_kill_base.png")
    
    # apply sigmoid corrections
    for metric_dict in offensive_metrics:
        metric_dict = apply_sigmoid_correction(metric_dict, True)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Shots Against"], offensive_metrics[0])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Shots Against"], max(list(offensive_metrics[0].values())),
        min(list(offensive_metrics[0].values())), sigmiod_ticks,
        "Graphs/offensive_Rating/shots_against_per_game_sigmoid.png")
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Goals Against"], offensive_metrics[1])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Goals Against"], max(list(offensive_metrics[1].values())),
        min(list(offensive_metrics[1].values())), sigmiod_ticks,
        "Graphs/offensive_Rating/goals_against_per_game_sigmoid.png")
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Penalty Kill"], offensive_metrics[2])
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "Penalty Kill"], max(list(offensive_metrics[2].values())),
        min(list(offensive_metrics[2].values())), sigmiod_ticks,
        "Graphs/offensive_Rating/penalty_kill_sigmoid.png")

    # combine metrics to overall score and plot
    offensive_rating_combine_metrics(offensive_metrics)
    write_out_file("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "offensive Rating"], offensive_rating_get_dict())
    plot_data_set("Output_Files/Instance_Files/offensiveRating.csv",
        ["Team", "offensive Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/offensive_Rating/offensive_rating_final.png")

def calculate_defensive_rating() -> None:
    defensive_metrics = defensive_rating_get_data_set()

    # plot each metric before sigmoid
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Shots Against"], defensive_metrics[0])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Shots Against"], min(list(defensive_metrics[0].values())),
        max(list(defensive_metrics[0].values())), [],
        "Graphs/Defensive_Rating/shots_against_per_game_base.png")
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Goals Against"], defensive_metrics[1])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Goals Against"], min(list(defensive_metrics[1].values())),
        max(list(defensive_metrics[1].values())), [],
        "Graphs/Defensive_Rating/goals_against_per_game_base.png")
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Penalty Kill"], defensive_metrics[2])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Penalty Kill"], min(list(defensive_metrics[2].values())),
        max(list(defensive_metrics[2].values())), [],
        "Graphs/Defensive_Rating/penalty_kill_base.png")
    
    # apply sigmoid corrections
    for metric_dict in defensive_metrics:
        metric_dict = apply_sigmoid_correction(metric_dict, True)

    # plot individual metrics after sigmoid
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Shots Against"], defensive_metrics[0])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Shots Against"], max(list(defensive_metrics[0].values())),
        min(list(defensive_metrics[0].values())), sigmoid_ticks,
        "Graphs/Defensive_Rating/shots_against_per_game_sigmoid.png")
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Goals Against"], defensive_metrics[1])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Goals Against"], max(list(defensive_metrics[1].values())),
        min(list(defensive_metrics[1].values())), sigmiod_ticks,
        "Graphs/Defensive_Rating/goals_against_per_game_sigmoid.png")
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Penalty Kill"], defensive_metrics[2])
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Penalty Kill"], max(list(defensive_metrics[2].values())),
        min(list(defensive_metrics[2].values())), sigmiod_ticks,
        "Graphs/Defensive_Rating/penalty_kill_sigmoid.png")

    # combine metrics to overall score and plot
    defensive_rating_combine_metrics(defensive_metrics)
    write_out_file("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating"], defensive_rating_get_dict())
    plot_data_set("Output_Files/Instance_Files/DefensiveRating.csv",
        ["Team", "Defensive Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Defensive_Rating/defensive_rating_final.png")

def calculate_clutch_rating() -> None:

    # first calculate the positive part of the clutch rating
    clutch_calculate_lead_protection()

    # finally combine the factors, write out, and plot
    clutch_rating = apply_sigmoid_correction(clutch_rating_get_dict())
    write_out_file("Output_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating"], clutch_rating)
    plot_data_set("Output_Files/Instance_Files/ClutchRating.csv",
        ["Team", "Clutch Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Clutch_Rating/clutch_rating_final.png")


def calculate_recent_form() -> None:
    
    # first calculate the recent form raw rating and plot
    recent_form_calculate_rating()
    write_out_file("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], recent_form_get_dict())
    plot_data_set("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Recent_Form/recent_form_base.png")

    # now apply the sigmoid correction and plot
    recent_form_rating = apply_sigmoid_correction(recent_form_get_dict())
    write_out_file("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], recent_form_rating)
    plot_data_set("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Recent_Form/recent_form_final.png")


'''
Function to create the combined set of all metrics into one ranking score
'''
def combine_all_factors() -> None:
    
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
    plot_data_set("Output_Files/Instance_Files/TotalRating.csv",
        ["Team", "Total Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Final_Rating_Score/final_rating_score.png")

'''
Specialized functions to calculate all metrics and update trend files, used in
    isolation
'''
def average_ranking_trends() -> None:

    # calculate the total ranking
    calculate_recent_form()
    calculate_strenght_of_schedule()
    calculate_win_rating()
    calculate_clutch_rating()
    calculate_offensive_rating()
    calculate_defensive_rating()
    combine_all_factors()

    absolute_rankings_update(total_rating)
    average_rankings_update(total_rating, ranking_absolutes)


def absolute_ranking_trends() -> None:

    # calculate the total ranking
    calculate_recent_form()
    calculate_strenght_of_schedule()
    calculate_win_rating()
    calculate_clutch_rating()
    calculate_offensive_rating()
    calculate_defensive_rating()
    combine_all_factors()

    absolute_rankings_update(total_rating)


if __name__ == "__main__":
    
    # get a command from the user
    command = input("Welcome, Enter Command:\n\t" + "(re)cent\n\t" +
        "(st)rength\n\t" + "(w)ins\n\t" + "(sc)oring\n\t" + "(c)lutch\n\t" +
        "(sp)ecial\n\t" + "(av)erage ranking\n\t" + "(ab)solute ranking\n\t" +
        "(a)ll\n\t" + "(e)xit\n" + ">")

    # regardless of command parse the input files
    parse_all_data_files()

    while (command != "e"):
    
        # handle the user command
        if command == 're':
            calculate_recent_form()
        
        elif command == 'st':
            calculate_strenght_of_schedule()

        elif command == 'w':
            calculate_win_rating()

        elif command == 'c':
            calculate_clutch_rating()

        elif command == 'av':
            average_ranking_trends()

        elif command == 'ab':
            absolute_ranking_trends()

        elif command == 'a':

            # calculate all the elements of the score and plot them
            calculate_recent_form()
            calculate_strenght_of_schedule()
            calculate_win_rating()
            calculate_clutch_rating()
            calculate_offensive_rating()
            calculate_defensive_rating()

            # combine all factors and plot the total rankings
            combine_all_factors()

            # write out and plot all high level trend files
            # strength of schedule
            update_trend_file("Output_Files/Trend_Files/StrengthOfSchedule.csv",
                strength_of_schedule_get_dict())
            plot_trend_set("Output_Files/Trend_Files/StrengthOfSchedule.csv",
                ["Rating Date", "Strength of Schedule"], 1.1, -.1,
                sigmiod_ticks,
                "Graphs/Strength_of_Schedule/strength_of_schedule_trend.png")

            # win rating
            update_trend_file("Output_Files/Trend_Files/WinRating.csv",
                win_rating_get_dict())
            plot_trend_set("Output_Files/Trend_Files/WinRating.csv",
                ["Rating Date", "Win Rating"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Win_Rating/win_rating_trend.png")

            # clutch_rating
            update_trend_file("Output_Files/Trend_Files/ClutchRating.csv",
                clutch_rating_get_dict())
            plot_trend_set("Output_Files/Trend_Files/ClutchRating.csv",
                ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Clutch_Rating/clutch_rating_trend.png")

            # update the trend file
            update_trend_file("Output_Files/Trend_Files/RecentForm.csv",
                recent_form_get_dict())
            plot_trend_set("Output_Files/Trend_Files/RecentForm.csv",
                ["Rating Date", "Recent Form"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Recent_Form/recent_form_trend.png")

            # ratings score
            update_trend_file("Output_Files/Trend_Files/RatingScore.csv",
                total_rating)
            plot_trend_set("Output_Files/Trend_Files/RatingScore.csv",
                ["Rating Date", "Rating Score"], 1, 0, sigmiod_ticks,
                "Graphs/Final_Rating_Score/rating_score_trend.png")

            # absolute rating
            absolute_rankings_update(total_rating)
            update_trend_file("Output_Files/Trend_Files/AbsoluteRankings.csv",
                ranking_absolutes)
            plot_trend_set("Output_Files/Trend_Files/AbsoluteRankings.csv",
                ["Rating Date", "Absolute Ranking"], 0, 33, range(1, 33, 1),
                "Graphs/Final_Rating_Score/absolute_ranking_trend.png")

            # average rankings
            average_rankings_update(total_rating, ranking_absolutes)
            update_trend_file("Output_Files/Trend_Files/AverageRankings.csv",
                ranking_averages)
            plot_trend_set("Output_Files/Trend_Files/AverageRankings.csv",
                ["Rating Date", "Average Ranking"], 0, 33, range(1, 33, 1),
                "Graphs/Final_Rating_Score/average_ranking_trend.png")

        elif command == 'e':
            exit()

        command = input(">")
