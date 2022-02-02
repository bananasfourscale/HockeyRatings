import csv

def write_out_file(file_name : str = "", header_row : list = [],
                   rating_list : dict = {}) -> None:

    with open(file_name, 'w', newline='') as csv_data_file:
        csv_writer = csv.writer(csv_data_file, delimiter = '\t', quotechar='|', 
            quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header_row)
        for team in rating_list.keys():
            csv_writer.writerow([team, str(rating_list[team])])
            # print("{} : {}".format(team, str(rating_list[team])))