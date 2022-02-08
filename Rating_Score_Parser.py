import csv
import datetime
from Weights import VERSION_MAJOR, VERSION_MINOR, divisions


def rating_score_write_out(total_ratings : dict = {}) -> None:
    date = str(datetime.datetime.now())
    date_split = date.split(" ")
    date_split = date_split[0].split("-")

    # get the current date and version for that column
    date_rating = date_split[2] + "/" + date_split[1] + "/" + date_split[0] + \
        " (v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + ")"
    
    with open("Input_Files/RatingScore.csv", 'a', newline='') as csv_date_file:
        csv_writer = csv.writer(csv_date_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # for each team print the rating with this timestamp
        for team in total_ratings.keys():
            csv_writer.writerow([date_rating, team, divisions[team],
                total_ratings[team]])
    

if __name__ == "__main__":
    pass
