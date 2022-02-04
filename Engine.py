# import all assisting built in modules
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter
from enum import Enum

# import all custom modules for parsing
from Ranking_Averages_Parser import *
from Team_Summary_Parser import *
from Matches_Parser import *
from Leading_Trailing_Parser import *
from Last_Ten_Parser import *
from CSV_Writer import *

# import all custom modules for statistical analysis
from Strength_of_Schedule import *
from Win_Rating import *
from Scoring_Rating import *
from Special_Teams import *
from Clutch import *
from RecentForm import *

class total_rating_weights(Enum):
    WIN_RATING_WEIGHT = 0.5
    SCORING_RATING_WEIGHT = 0.05
    SPECIAL_TEAMS_RATING_WEIGHT = 0.08
    CLUTCH_RATING_WEIGHT = 0.12
    FORM_RATING_WEIGHT = 0.12
    SOS_RATING_WEIGHT = 0.13

colors = [
    "#F47A38", "#8C2633", "#FFB81C", "#002654", "#C8102E", "#CC0000", "#CF0A2C",
    "#6F263D", "#002654", "#006847", "#CE1126", "#FF4C00", "#B9975B", "#572A84",
    "#154734", "#AF1E2D", "#FFB81C", "#CE1126", "#FF4C00", "#0038A8", "#C52032",
    "#F74902", "#CFC493", "#006D75", "#001628", "#002F87", "#002868", "#00205B",
    "#00843D", "#B4975A", "#C8102E", "#8E9090"
]

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
    'Montreal Canadiens' : 0,
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

def plot_data_set(csv_file : str = "", axis : list = [],
                  upper_bound : float = 0.0, lower_bound : float = 0.0,
                  tick_set : list = [], image_file : str = "", label = False) \
                                                                        -> None:
    plot_data = pd.read_csv(csv_file, delimiter='\t')
    sns.set_theme()
    team_palette = sns.color_palette(colors)
    plot = sns.barplot(data=plot_data, x=axis[0], y=axis[1],
        palette=team_palette)
    plot.set(xticks=range(len(colors)))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    if label:
        pass
        # for index, row in plot_data.iterrows():
        #     plot.text(row.name, round(row[1],2), round(row[1],2),
        #         color='black', ha="center")

        #for row in plot_data:

    plotter.tight_layout()
    plotter.ylim(lower_bound, upper_bound)
    if len(tick_set) > 0:
        plotter.yticks(tick_set)
    plotter.savefig(image_file)
    plotter.clf()

def parse_all_data_files() -> None:
    parse_average_ratings('Input_Files/AverageRatings.csv')
    parse_average_rating_header_row(average_ratings_header)
    parse_matches('Input_Files/Matches2021_2022.csv')
    read_matches(matches)
    parse_team_summary('Input_Files/TeamSummary.csv')
    parse_leading_trailing('Input_Files/LeadingTrailing.csv')
    parse_last_ten("Input_Files/Last10Games.csv")


def calculate_strenght_of_schedule() -> None:

    # write the results out to file and graph
    write_out_file("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 500, -500, [],
        "Graphs/Strength_of_Schedule/sos_base.png", False)

    # scale the strength of schedule by game, write out again, and graph
    strength_of_schedule_scale_by_game()
    write_out_file("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 15.0, -15.0, [],
        "Graphs/Strength_of_Schedule/sos_game_scale.png", False)

    # apply sigmoid correction, write out again, and graph
    strength_of_schedule_apply_sigmoid()
    write_out_file("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], strength_of_schedule)
    plot_data_set("Output_Files/StengthOfSchedule.csv",
        ["Team", "Strength of Schedule"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Strength_of_Schedule/sos_sigmoid_corrected.png", False)


def calculate_win_rating() -> None:

    # calculate the win rating and graph
    win_rating_calc()
    write_out_file("Output_Files/WinRating.csv", ["Team", "Win Rating"],
        win_rating)
    plot_data_set("Output_Files/WinRating.csv", ["Team", "Win Rating"], 1.0,
        0.0, sigmiod_ticks, "Graphs/Win_Rating/win_rating.png", False)


def calculate_scoring_rating() -> None:

    # calculate the goal difference and graph
    scoring_rating_calc_goal_diff()
    write_out_file("Output_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], scoring_difference)
    plot_data_set("Output_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], 2.0, -2.0, [],
        "Graphs/Scoring_Rating/scoring_diff_base.png", False)

    # apply a sigmoid correction and graph again
    scoring_rating_apply_sigmoid_goal_diff()
    write_out_file("Output_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], scoring_difference)
    plot_data_set("Output_Files/ScoringDiff.csv",
        ["Team", "Scoring Difference"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Scoring_Rating/shooting_diff.png", False)

    # calculate the shooting diff and graph
    scoring_rating_calc_shooting_diff()
    write_out_file("Output_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], shooting_difference)
    plot_data_set("Output_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], 12.0, -12.0, [],
        "Graphs/Scoring_Rating/shooting_diff_base.png", False)

    # apply a signmoid correction and graph again
    scoring_rating_apply_sigmoid_shooting_diff()
    write_out_file("Output_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], shooting_difference)
    plot_data_set("Output_Files/ShootingDiff.csv",
        ["Team", "Shooting Difference"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Scoring_Rating/shooting_diff.png", False)

    # combine the scoring rating factors and graph again
    scoring_rating_combine_factors()
    write_out_file("Output_Files/ScoringRating.csv", ["Team", "Scoring Rating"],
        scoring_rating)
    plot_data_set("Output_Files/ScoringRating.csv", ["Team", "Scoring Rating"],
        1.0, 0.0, sigmiod_ticks, "Graphs/Scoring_Rating/scoring_rating.png",
        False)


def calculate_special_teams_rating() -> None:

    # combine special teams and plot
    special_teams_combine()
    write_out_file("Output_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], special_teams)
    plot_data_set("Output_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], 130, 50, [],
        "Graphs/Special_Teams/special_teams_combined.png", False)

    # apply sigmoid correction and plot
    special_teams_apply_sigmoid()
    write_out_file("Output_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], special_teams)
    plot_data_set("Output_Files/SpecialTeams.csv",
        ["Team", "Special Teams"], 1.0, 0.0, sigmiod_ticks,
        "Graphs/Special_Teams/special_teams_corrected.png", False)


def calculate_clutch_rating() -> None:

    # first calculate the positive part of the clutch rating
    clutch_calculate_lead_protection()
    
    # next calculate the negative part of the clutch rating
    clutch_calculated_trail_comeback()

    # finally combine the factors, write out, and plot
    clutch_apply_sigmoid()
    write_out_file("Output_Files/ClutchRating.csv", ["Team", "Clutch Rating"],
        clutch_rating)
    plot_data_set("Output_Files/ClutchRating.csv", ["Team", "Clutch Rating"],
        1.0, 0.0, sigmiod_ticks,
        "Graphs/ClutchRating/clutch_rating_corrected.png", False)


def calculate_recent_form() -> None:
    
    # first calculate the recent form raw rating and plot
    form_calculate_rating()
    write_out_file("Output_Files/RecentForm.csv", ["Team", "Recent Form"],
        recent_form_rating)
    plot_data_set("Output_Files/RecentForm.csv", ["Team", "Recent Form"],
        10.0, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Graphs/FormRating/recent_form_base.png", False)

    # now apply the sigmoid correction and plot
    form_apply_sigmoid()
    write_out_file("Output_Files/RecentForm.csv", ["Team", "Recent Form"],
        recent_form_rating)
    plot_data_set("Output_Files/RecentForm.csv", ["Team", "Recent Form"],
        1.0, 0.0, sigmiod_ticks, "Graphs/FormRating/recent_form_corrected.png",
        False)


def combine_all_factors() -> None:
    
    # calculate the final rating for all teams using the forms above
    for team in total_rating.keys():
        total_rating[team] = \
            (win_rating[team] * \
                total_rating_weights.WIN_RATING_WEIGHT.value) + \
            (scoring_rating[team] * \
                total_rating_weights.SCORING_RATING_WEIGHT.value) + \
            (special_teams[team] * \
                total_rating_weights.SPECIAL_TEAMS_RATING_WEIGHT.value) + \
            (clutch_rating[team] * \
                total_rating_weights.CLUTCH_RATING_WEIGHT.value) + \
            (recent_form_rating[team] * \
                total_rating_weights.FORM_RATING_WEIGHT.value) + \
            (strength_of_schedule[team] * \
                total_rating_weights.SOS_RATING_WEIGHT.value)

    # write out and plot the total ratings
    write_out_file("Output_Files/TotalRating.csv", ["Team", "Total Rating"],
        total_rating)
    plot_data_set("Output_Files/TotalRating.csv", ["Team", "Total Rating"],
        1.0, 0.0, sigmiod_ticks, "Graphs/total_rating.png", False)


if __name__ == "__main__":
    
    # get a command from the user
    command = input("Welcome, Enter Command:\n\t" + "(r)ecent\n\t" +
        "(st)rength\n\t" + "(w)ins\n\t" + "(sc)oring\n\t" + "(c)lutch\n\t" +
        "(sp)ecial\n\t" + "(a)ll\n\t" "(e)xit\n" + ">")

    # regardless of command parse the input files
    parse_all_data_files()

    while (command != "e"):
    
        # handle the user command
        if command == 'r':
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

        elif command == 'a':
            calculate_recent_form()
            calculate_strenght_of_schedule()
            calculate_win_rating()
            calculate_scoring_rating()
            calculate_clutch_rating()
            calculate_special_teams_rating()
            combine_all_factors()

        elif command == 'e':
            exit()

        command = input(">")
