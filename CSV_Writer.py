import csv
import datetime
from encodings.utf_8 import encode
from Weights import *

def write_out_file(file_name : str = "", header_row : list = [],
                   rating_list : dict = {}) -> None:

    with open(file_name, 'w', newline='', encoding='utf-8') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for key in rating_list.keys():
            # if (team == "Montréal Canadiens") :
            csv_writer.writerow([key, str(rating_list[key])])
            # print("{} : {}".format(team, str(rating_list[team])))


def update_trend_file(file_name : str = "", stat_dict : dict = {}) -> None:
    date = str(datetime.datetime.now())
    date_split = date.split(" ")
    date_split = date_split[0].split("-")

    # get the current date and version for that column
    date_rating = date_split[2] + "/" + date_split[1] + "/" + date_split[0] + \
        " (v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + ")"
    with open(file_name, 'a+', newline='', encoding='utf-8') as csv_date_file:
        csv_writer = csv.writer(csv_date_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # for each team print the rating with this timestamp
        for key in stat_dict.keys():
            if type(stat_dict[key]) == list:
                csv_writer.writerow([date_rating, key, divisions[key],
                    stat_dict[key][len(stat_dict[key])-1]])
            else:
                csv_writer.writerow([date_rating, key, divisions[key],
                    stat_dict[key]])