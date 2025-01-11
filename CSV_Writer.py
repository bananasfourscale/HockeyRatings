import csv
from Weights import divisions, VERSION_MAJOR, VERSION_MINOR


def write_out_file(file_name : str = "", header_row : list = [],
    rating_list : dict = {}) -> None:

    with open(file_name, 'w', newline='', encoding='utf-16') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for key in rating_list.keys():
            csv_writer.writerow([key, str(rating_list[key])])
        csv_data_file.close()


def write_out_player_file(file_name : str = "", header_row : list = [],
    rating_list : dict = {}, player_team_list : dict = {}, ascending=True) \
                                                                        -> None:

    with open(file_name, 'w', newline='', encoding='utf-16') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter='\t', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # sort player dict
        sorted_list = \
            dict(sorted(rating_list.items(), key=lambda item: item[1],
                reverse=ascending))

        # for each player print the player, the stat and the team they're on
        csv_writer.writerow(header_row)
        count = 0
        prev_data = float('inf')
        streak = 1
        for key in sorted_list.keys():
            if rating_list[key] != prev_data:
                count += streak
                streak = 1
            else:
                streak += 1
            prev_data = rating_list[key]
            data_list = \
                [str(count) + " " + key.replace("", "c"), rating_list[key],
                    player_team_list[key]]
            csv_writer.writerow(data_list)
        csv_data_file.close()


def update_trend_file(file_name : str = "", stat_dict : dict = {},
    rating_type : str="") -> None:
    
    # construct the header row in case the file is new
    header_row = ["Rating Date", "Team", "Division", rating_type]
    with open(file_name, 'w', newline='', encoding='utf-16') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        
        # first write out the header row
        csv_writer.writerow(header_row)
        
        # now cycle through each date in the given trend data set and writes
        for date in stat_dict.keys():

            # split the given trend date into its parts (yyyy-mm-dd)
            if date.find('-') == -1:
                break
            date_split = date.split("-")

            # get the current date and version for that column
            date_rating = date_split[2] + "/" + date_split[1] + "/" + \
                date_split[0] + " (v" + str(VERSION_MAJOR) + "." + \
                str(VERSION_MINOR) + ")"
            
            # for each team print the rating with this timestamp 
            for team in stat_dict[date].keys():
                csv_writer.writerow([date_rating, team, divisions[team],
                    stat_dict[date][team]])
        csv_data_file.close()


def write_out_matches_file(file_name : str = "", header_row : list = [],
    rating_order : list=[], rating_list : list=[]) -> None:

    with open(file_name, 'w', newline='', encoding='utf-16') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for i in range(0, len(rating_list) - 1, 2):
            row = [rating_order[int(i / 2)], rating_list[i], rating_list[i + 1]]
            csv_writer.writerow(row)
        csv_data_file.close()