# import all assisting built in modules
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter

# import all custom modules for parsing
from Ranking_Averages_Parser import *
from Team_Summary_Parser import *
from Matches_Parser import *

# import all custom modules for statistical analysis
from Strength_of_Schedule import *

colors = [
    "#F47A38", "#8C2633", "#FFB81C", "#002654", "#C8102E", "#CC0000", "#CF0A2C",
    "#6F263D", "#002654", "#006847", "#CE1126", "#FF4C00", "#B9975B", "#572A84",
    "#154734", "#AF1E2D", "#FFB81C", "#CE1126", "#FF4C00", "#0038A8", "#C52032",
    "#F74902", "#CFC493", "#006D75", "#001628", "#002F87", "#002868", "#00205B",
    "#00843D", "#B4975A", "#C8102E", "#8E9090"
]

sigmiod_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

def parse_all_data_files():
    parse_average_ratings('Input_Files/AverageRatings.csv')
    parse_average_rating_header_row(average_ratings_header)
    parse_matches('Input_Files/Matches2021_2022.csv')
    parse_team_summary('Input_Files/TeamSummary.csv')

def calculate_strenght_of_schedule():
    read_matches(matches)
    strength_of_schedule_write_out()
    ranking_averages_data = pd.read_csv("Output_Files/StengthOfSchedule.csv",
        delimiter='\t')

    sns.set_theme()
    team_palette = sns.color_palette(colors)
    plot = sns.barplot(data=ranking_averages_data, x="Team",
        y="Strength of Schedule", palette=team_palette)
    plot.set(xticks=range(len(colors)))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    plotter.tight_layout()
    plotter.ylim(-500, 500)
    plotter.savefig("graphs/sos_base.png")
    plotter.clf()


    strength_of_schedule_scale_by_game()
    strength_of_schedule_write_out()
    ranking_averages_data = pd.read_csv("Output_Files/StengthOfSchedule.csv",
        delimiter='\t')

    sns.set_theme()
    team_palette = sns.color_palette(colors)
    plot = sns.barplot(data=ranking_averages_data, x="Team",
        y="Strength of Schedule", palette=team_palette)
    plot.set(xticks=range(len(colors)))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    plotter.tight_layout()
    plotter.ylim(-15, 15)
    plotter.savefig("graphs/sos_game_scale.png")
    plotter.clf()


    strength_of_schedule_apply_sigmoid()
    strength_of_schedule_write_out()
    ranking_averages_data = pd.read_csv("Output_Files/StengthOfSchedule.csv",
        delimiter='\t')

    sns.set_theme()
    team_palette = sns.color_palette(colors)
    plot = sns.barplot(data=ranking_averages_data, x="Team",
        y="Strength of Schedule", palette=team_palette)
    plot.set(xticks=range(len(colors)))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    plotter.tight_layout()
    plotter.ylim(0, 1.0)
    plotter.yticks(sigmiod_ticks)
    plotter.savefig("graphs/sos_sigmoid_corrected.png")
    plotter.clf()

if __name__ == "__main__":

    parse_all_data_files()

    calculate_strenght_of_schedule()
