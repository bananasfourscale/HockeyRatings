import csv
import datetime
from Weights import divisions, VERSION_MAJOR, VERSION_MINOR


def write_out_file(file_name : str = "", header_row : list = [],
                   rating_list : dict = {}) -> None:
    with open(file_name, 'w', newline='', encoding='utf-8') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for key in rating_list.keys():
            csv_writer.writerow([key, str(rating_list[key])])


def write_out_player_file(file_name : str = "", header_row : list = [],
                          rating_list : dict = {}, player_list : dict = {},
                          ascending=True) \
                                                                    -> None:
    with open(file_name, 'w', newline='', encoding='utf-8') as csv_date_file:
        csv_writer = csv.writer(csv_date_file, delimiter='\t', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # sort player dict
        sorted_list = \
            dict(sorted(rating_list.items(), key=lambda item: item[1],
                reverse=ascending))

        # for each player print the player, the stat and the team they're on
        csv_writer.writerow(header_row)
        count = 1
        for key in sorted_list.keys():
            data_list = \
                [str(count) + " " + key, rating_list[key], player_list[key][1]]
            csv_writer.writerow(data_list)
            count += 1


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