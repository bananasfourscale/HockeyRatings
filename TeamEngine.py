# import all assisting built in modules
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter

# import all custom modules for parsing
from Parsers.Average_Ranking_Parser import *
from Parsers.Absolute_Ranking_Parser import *
from Parsers.Team_Summary_Parser import *
from Parsers.Matches_Parser import *
from Parsers.Leading_Trailing_Parser import *
from CSV_Writer import *

# import all custom modules for statistical analysis
from Metrics.Strength_of_Schedule import *
from Metrics.Win_Rating import *
from Metrics.Scoring_Rating import *
from Metrics.Special_Teams import get_special_teams_dict, special_teams_combine
from Metrics.Clutch import *
from Metrics.Recent_Form import *
from Metrics.Sigmoid_Correction import apply_sigmoid_correction

from Weights import *


team_color_hex_codes = [
    "#F47A38", "#8C2633", "#FFB81C", "#ADAFFA", "#C8102E", "#CC0000", "#CF0A2C",
    "#6F263D", "#002654", "#006847", "#CE1126", "#FF4C00", "#B9975B", "#572A84",
    "#154734", "#AF1E2D", "#FFB81C", "#000000", "#FF4C00", "#0038A8", "#C52032",
    "#C83C01", "#CFC493", "#006D75", "#001628", "#002F87", "#FFFFFF", "#00205B",
    "#00843D", "#B4975A", "#C8102E", "#8E9090"
]

sigmiod_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

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
def plot_data_set(csv_file : str = "", axis : list = [],
                  upper_bound : float = 0.0, lower_bound : float = 0.0,
                  tick_set : list = [], image_file : str = "") -> None:
    plot_data = pd.read_csv(csv_file, delimiter='\t', encoding='utf-8')
    sns.set_theme()
    team_palette = sns.color_palette(team_color_hex_codes)
    plot = sns.barplot(data=plot_data, x=axis[0], y=axis[1],
        palette=team_palette)
    plot.set(xticks=range(len(team_color_hex_codes)))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    plotter.tight_layout()
    plotter.ylim(lower_bound, upper_bound)
    if len(tick_set) > 0:
        plotter.yticks(tick_set)
    plotter.savefig(image_file)
    plotter.clf()


def plot_trend_set(csv_file : str = "", axis : list = [],
                   upper_bound : float = 0.0, lower_bound : float = 0.0,
                   tick_set : list = [], image_file : str = "") -> None:
    plot_data = pd.read_csv(csv_file, delimiter=',', encoding='utf-8')
    sns.set_theme()
    plotter.figure(figsize=(25, 10), dpi=100)
    team_palette = sns.color_palette(team_color_hex_codes)
    plot = sns.lineplot(data=plot_data, x=axis[0], y=axis[1],
        hue="Team", style="Division",palette=team_palette, marker='s')
    plot.set(yticks=tick_set)
    plotter.tick_params(axis='x', which='major', labelsize=8)
    plotter.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plotter.ylim(lower_bound, upper_bound)
    plotter.savefig(image_file, bbox_inches='tight')
    plotter.clf()

'''
Combined specialized parser to get cumulative data needed all ranking factors
'''
def parse_all_data_files() -> None:
    average_rankings_parse('Output_Files/Trend_Files/AverageRankings.csv')
    absolute_rankings_parse('Output_Files/Trend_Files/AbsoluteRankings.csv')
    parse_matches('Input_Files/Matches2021_2022.csv')
    read_matches(matches)
    parse_team_summary('Input_Files/TeamSummary.csv')
    parse_leading_trailing('Input_Files/LeadingTrailing.csv')

'''
Helper functions that calculate the various factors used to create the final
    ranking score
'''
def calculate_strenght_of_schedule() -> None:

    # write the results out to file and graph
    write_out_file("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 500, -500, [],
        "Graphs/Strength_of_Schedule/sos_base.png")

    # scale the strength of schedule by game, write out again, and graph
    strength_of_schedule_scale_by_game()
    write_out_file("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 15.0, -15.0, [],
        "Graphs/Strength_of_Schedule/sos_game_scale.png")

    # apply sigmoid correction, write out again, and graph
    strength_of_schedule_apply_sigmoid()
    write_out_file("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/Instance_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Strength_of_Schedule/strenght_of_schedule_final.png")


def calculate_win_rating() -> None:

    # calculate the win rating and graph
    win_rating_calc()
    write_out_file("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating"], win_rating)
    plot_data_set("Output_Files/Instance_Files/WinRating.csv",
        ["Team", "Win Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Win_Rating/win_rating_final.png")


def calculate_scoring_rating() -> None:

    # calculate the goal difference and graph
    scoring_rating_calc_goal_diff()
    write_out_file("Output_Files/Instance_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], scoring_difference)
    plot_data_set("Output_Files/Instance_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], 2.0, -2.0, [],
        "Graphs/Scoring_Rating/scoring_diff_base.png")

    # apply a sigmoid correction and graph again
    scoring_rating_apply_sigmoid_goal_diff()
    write_out_file("Output_Files/Instance_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], scoring_difference)
    plot_data_set("Output_Files/Instance_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Scoring_Rating/scoring_diff_sigmoid_corrected.png")

    # calculate the shooting diff and graph
    scoring_rating_calc_shooting_diff()
    write_out_file("Output_Files/Instance_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], shooting_difference)
    plot_data_set("Output_Files/Instance_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], 12.0, -12.0, [],
        "Graphs/Scoring_Rating/shooting_diff_base.png")

    # apply a signmoid correction and graph again
    scoring_rating_apply_sigmoid_shooting_diff()
    write_out_file("Output_Files/Instance_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], shooting_difference)
    plot_data_set("Output_Files/Instance_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Scoring_Rating/shooting_diff_sigmoid_corrected.png")

    # combine the scoring rating factors and graph again
    scoring_rating_combine_factors()
    write_out_file("Output_Files/Instance_Files/ScoringRating.csv",
        ["Team", "Scoring Rating"], scoring_rating)
    plot_data_set("Output_Files/Instance_Files/ScoringRating.csv",
        ["Team", "Scoring Rating"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Scoring_Rating/scoring_rating_final.png")


def calculate_special_teams_rating() -> None:

    # combine special teams and plot
    special_teams_combine()
    write_out_file("Output_Files/Instance_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], get_special_teams_dict())
    plot_data_set("Output_Files/Instance_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], 130, 50, [],
        "Graphs/Special_Teams/special_teams_combined.png")

    # apply sigmoid correction and plot
    special_teams = apply_sigmoid_correction(get_special_teams_dict())
    write_out_file("Output_Files/Instance_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], special_teams)
    plot_data_set("Output_Files/Instance_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Special_Teams/special_teams_final.png")

    update_trend_file("Output_Files/Trend_Files/SpecialTeams.csv",
        get_special_teams_dict())
    plot_trend_set("Output_Files/Trend_Files/SpecialTeams.csv",
        ["Rating Date", "Special Teams"], 1.1, -.1, sigmiod_ticks,
        "Graphs/Special_Teams/special_teams_trend.png")


def calculate_clutch_rating() -> None:

    # first calculate the positive part of the clutch rating
    clutch_calculate_lead_protection()
    
    # next calculate the negative part of the clutch rating
    clutch_calculated_trail_comeback()

    # finally combine the factors, write out, and plot
    clutch_apply_sigmoid()
    write_out_file("Output_Files/Instance_Files/ClutchRating.csv", ["Team", "Clutch Rating"],
        clutch_rating)
    plot_data_set("Output_Files/Instance_Files/ClutchRating.csv", ["Team", "Clutch Rating"],
        1.0, 0.0, sigmiod_ticks,
        "Graphs/Clutch_Rating/clutch_rating_final.png")


def calculate_recent_form() -> None:
    
    # first calculate the recent form raw rating and plot
    recent_form_calculate_rating()
    write_out_file("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], recent_form_rating)
    plot_data_set("Output_Files/Instance_Files/RecentForm.csv",
        ["Team", "Recent Form"], 10.0, 0,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/Recent_Form/recent_form_base.png")

    # now apply the sigmoid correction and plot
    recent_form_apply_sigmoid()
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
            (win_rating[team] * \
                total_rating_weights.WIN_RATING_WEIGHT.value) + \
            (scoring_rating[team] * \
                total_rating_weights.SCORING_RATING_WEIGHT.value) + \
            (get_special_teams_dict()[team] * \
                total_rating_weights.SPECIAL_TEAMS_RATING_WEIGHT.value) + \
            (clutch_rating[team] * \
                total_rating_weights.CLUTCH_RATING_WEIGHT.value) + \
            (recent_form_rating[team] * \
                total_rating_weights.FORM_RATING_WEIGHT.value) + \
            (strength_of_schedule[team] * \
                total_rating_weights.SOS_RATING_WEIGHT.value)

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
    calculate_scoring_rating()
    calculate_clutch_rating()
    calculate_special_teams_rating()
    combine_all_factors()

    absolute_rankings_update(total_rating)
    average_rankings_update(total_rating, ranking_absolutes)


def absolute_ranking_trends() -> None:

    # calculate the total ranking
    calculate_recent_form()
    calculate_strenght_of_schedule()
    calculate_win_rating()
    calculate_scoring_rating()
    calculate_clutch_rating()
    calculate_special_teams_rating()
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

        elif command == 'sc':
            calculate_scoring_rating()

        elif command == 'c':
            calculate_clutch_rating()

        elif command == 'sp':
            calculate_special_teams_rating()

        elif command == 'av':
            average_ranking_trends()

        elif command == 'ab':
            absolute_ranking_trends()

        elif command == 'a':

            # calculate all the elements of the score and plot them
            calculate_recent_form()
            calculate_strenght_of_schedule()
            calculate_win_rating()
            calculate_scoring_rating()
            calculate_clutch_rating()
            calculate_special_teams_rating()

            # combine all factors and plot the total rankings
            combine_all_factors()

            # Now update all trend files
            # strength of schedule
            update_trend_file("Output_Files/Trend_Files/StrengthOfSchedule.csv",
                strength_of_schedule)
            plot_trend_set("Output_Files/Trend_Files/StrengthOfSchedule.csv",
                ["Rating Date", "Strength of Schedule"], 1.1, -.1,
                sigmiod_ticks,
                "Graphs/Strength_of_Schedule/strength_of_schedule_trend.png")

            # special teams
            update_trend_file("Output_Files/Trend_Files/SpecialTeams.csv",
                get_special_teams_dict())
            plot_trend_set("Output_Files/Trend_Files/SpecialTeams.csv",
                ["Rating Date", "Special Teams"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Special_Teams/special_teams_trend.png")

            # clutch rating
            update_trend_file("Output_Files/Trend_Files/ClutchRating.csv",
                clutch_rating)
            plot_trend_set("Output_Files/Trend_Files/ClutchRating.csv",
                ["Rating Date", "Clutch Rating"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Clutch_Rating/clutch_rating_trend.png")

            # win rating
            update_trend_file("Output_Files/Trend_Files/WinRating.csv",
                win_rating)
            plot_trend_set("Output_Files/Trend_Files/WinRating.csv",
                ["Rating Date", "Win Rating"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Win_Rating/win_rating_trend.png")

            # scoring rating
            update_trend_file("Output_Files/Trend_Files/ScoringRating.csv",
                scoring_rating)
            plot_trend_set("Output_Files/Trend_Files/ScoringRating.csv",
                ["Rating Date", "Scoring Rating"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Scoring_rating/scoring_rating_trend.png")

            # recent form
            update_trend_file("Output_Files/Trend_Files/RecentForm.csv",
                recent_form_rating)
            plot_trend_set("Output_Files/Trend_Files/RecentForm.csv",
                ["Rating Date", "Recent Form"], 1.1, -.1, sigmiod_ticks,
                "Graphs/Recent_Form/recent_form_trend.png")

            # write out and plot all trend files\
            # ratings score
            update_trend_file("Output_Files/Trend_Files/RatingScore.csv", total_rating)
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
