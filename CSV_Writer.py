import csv
import datetime
from Weights import *

def write_out_file(file_name : str = "", header_row : list = [],
                   rating_list : dict = {}) -> None:

    with open(file_name, 'w', newline='') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for team in rating_list.keys():
            csv_writer.writerow([team, str(rating_list[team])])
            # print("{} : {}".format(team, str(rating_list[team])))


def update_trend_file(file_name : str = "", stat_dict : dict = {}) -> None:
    date = str(datetime.datetime.now())
    date_split = date.split(" ")
    date_split = date_split[0].split("-")

    # get the current date and version for that column
    date_rating = date_split[2] + "/" + date_split[1] + "/" + date_split[0] + \
        " (v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + ")"

    #print(ranking_averages)
    with open(file_name, 'a+', newline='') as csv_date_file:
        csv_writer = csv.writer(csv_date_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # for each team print the rating with this timestamp
        for team in stat_dict.keys():
            if type(stat_dict[team]) == list:
                csv_writer.writerow([date_rating, team, divisions[team],
                    stat_dict[team][len(stat_dict[team])-1]])
            else:
                csv_writer.writerow([date_rating, team, divisions[team],
                    stat_dict[team]])