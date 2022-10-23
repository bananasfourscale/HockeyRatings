# import all assisting built in modules
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plotter


team_color_hex_codes = [
    "#F47A38", "#8C2633", "#FFB81C", "#ADAFFA", "#C8102E", "#CC0000", "#CF0A2C",
    "#6F263D", "#002654", "#006847", "#CE1126", "#FF4C00", "#B9975B", "#572A84",
    "#154734", "#AF1E2D", "#FFB81C", "#000000", "#FF4C00", "#0038A8", "#C52032",
    "#C83C01", "#CFC493", "#006D75", "#001628", "#002F87", "#FFFFFF", "#00205B",
    "#00843D", "#B4975A", "#C8102E", "#8E9090"
]


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