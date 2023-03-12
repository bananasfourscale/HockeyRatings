# import all assisting built in modules
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter

team_color_hex_codes = {
    'Anaheim Ducks' : "#F47A38",
    'Arizona Coyotes' : "#8C2633",
    'Boston Bruins' : "#FFB81C",
    'Buffalo Sabres' : "#ADAFFA",
    'Calgary Flames' : "#C8102E",
    'Carolina Hurricanes' : "#CC0000",
    'Chicago Blackhawks' : "#CF0A2C",
    'Colorado Avalanche' : "#6F263D",
    'Columbus Blue Jackets' : "#002654",
    'Dallas Stars' : "#006847",
    'Detroit Red Wings' : "#CE1126",
    'Edmonton Oilers' : "#FF4C00",
    'Florida Panthers' : "#B9975B",
    'Los Angeles Kings' : "#572A84",
    'Minnesota Wild' : "#154734",
    'Montréal Canadiens' : "#AF1E2D",
    'Nashville Predators' : "#FFB81C",
    'New Jersey Devils' : "#000000",
    'New York Islanders' : "#FF4C00",
    'New York Rangers' : "#0038A8",
    'Ottawa Senators' : "#C52032",
    'Philadelphia Flyers' : "#C83C01",
    'Pittsburgh Penguins' : "#CFC493",
    'San Jose Sharks' : "#006D75",
    'Seattle Kraken' : "#001628",
    'St. Louis Blues' : "#002F87",
    'Tampa Bay Lightning' : "#CCCCFF",
    'Toronto Maple Leafs' : "#00205B",
    'Vancouver Canucks' : "#00843D",
    'Vegas Golden Knights' : "#B4975A",
    'Washington Capitals' : "#C8102E",
    'Winnipeg Jets' : "#8E9090",
}


def plot_data_set(csv_file : str = "", axis : list = [],
                  upper_bound : float = 0.0, lower_bound : float = 0.0,
                  tick_set : list = [], image_file : str = "",
                  ascending : bool=False) -> None:
    plot_data = pd.read_csv(csv_file, delimiter='\t', encoding='utf-16')
    plot_data = plot_data.sort_values(axis[1], ascending=ascending)
    sns.set_theme(font='Times New Roman')
    plotter.figure(figsize=(25, 10), dpi=100)
    player_color_sorted_list = []
    for player in plot_data.loc[:,"Team"]:
        player_color_sorted_list.append(team_color_hex_codes[player])
    team_palette = sns.color_palette(player_color_sorted_list)
    plot = sns.barplot(data=plot_data, x=axis[0], y=axis[1],
        palette=team_palette)
    plot.set(xticks=range(len(list(team_color_hex_codes.values()))))
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
        horizontalalignment='center')
    plotter.tick_params(axis='x', which='major', labelsize=24)
    plotter.tight_layout()

    # determine the bounds either based on the input, or based on the data set
    if (upper_bound == 0.0) and (lower_bound == 0.0):
        plot_min = \
            plot_data.min().loc[axis[1]] - (plot_data.min().loc[axis[1]] * 0.10)
        plot_max = \
            plot_data.max().loc[axis[1]] + (plot_data.min().loc[axis[1]] * 0.10)
        plotter.ylim(plot_min, plot_max)
    else:
        plotter.ylim(lower_bound, upper_bound)
    if len(tick_set) > 0:
        plotter.yticks(tick_set)
    plotter.savefig(image_file)
    plotter.clf()
    plotter.close()


def plot_trend_set(csv_file : str = "", axis : list = [],
                   upper_bound : float = 0.0, lower_bound : float = 0.0,
                   tick_set : list = [], image_file : str = "") -> None:
    plot_data = pd.read_csv(csv_file, delimiter=',', encoding='utf-8')
    sns.set_theme(font='Times New Roman')
    plotter.figure(figsize=(25, 10), dpi=100)
    team_palette = sns.color_palette(list(team_color_hex_codes.values()))
    plot = sns.lineplot(data=plot_data, x=axis[0], y=axis[1],
        hue="Team", style="Division",palette=team_palette, marker='s')
    plot.set(yticks=tick_set)
    plotter.tick_params(axis='x', which='major', labelsize=8)
    plotter.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plotter.ylim(lower_bound, upper_bound)
    plotter.savefig(image_file, bbox_inches='tight')
    plotter.clf()
    plotter.close()


def plot_player_ranking(csv_file : str = "", axis : list = [],
                        upper_bound : float = 0.0, lower_bound : float = 0.0,
                        tick_set : list = [], image_file : str = "",
                        ascending: bool=False) -> None:
    plot_data = pd.read_csv(csv_file, delimiter='\t', encoding='utf-16')
    plot_data = plot_data.sort_values(axis[1], ascending=ascending)
    sns.set_theme(font='Times New Roman')

    # determine the number of players to scale the graph accordingly
    num_players = plot_data.count().loc["Team"]
    plotter.figure(figsize=(20, num_players/4), dpi=100)

    # assign the correct Team color to each player in the list
    player_color_sorted_list = []
    for player in plot_data.loc[:,"Team"]:
        player_color_sorted_list.append(team_color_hex_codes[player])
    team_palette = sns.color_palette(player_color_sorted_list)

    # make player plots horizontal bar plots
    sns.barplot(data=plot_data, x=axis[1], y=axis[0], palette=team_palette)
    plotter.tick_params(axis='y', which='major', labelsize=12)
    plotter.tick_params(axis='x', which='major', labelsize=24)
    plotter.tight_layout()

    # determine the bounds either based on the input, or based on the data set
    if (upper_bound == 0.0) and (lower_bound == 0.0):
        plot_min = \
            plot_data.min().loc[axis[1]] - (plot_data.min().loc[axis[1]] * 0.10)
        plot_max = \
            plot_data.max().loc[axis[1]] + (plot_data.min().loc[axis[1]] * 0.10)
        plotter.xlim(plot_min, plot_max)
    else:
        plotter.xlim(lower_bound, upper_bound)
    if len(tick_set) > 0:
        plotter.xticks(tick_set)

    # save the figure to file and then close to save memory
    plotter.savefig(image_file, bbox_inches='tight')
    plotter.clf()
    plotter.close()
