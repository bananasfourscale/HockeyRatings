import csv
import datetime
from Weights import VERSION_MAJOR, VERSION_MINOR, divisions

ranking_averages = {
    'Anaheim Ducks' : [],
    'Arizona Coyotes' : [],
    'Boston Bruins' : [],
    'Buffalo Sabres' : [],
    'Calgary Flames' : [],
    'Carolina Hurricanes' : [],
    'Chicago Blackhawks' : [],
    'Colorado Avalanche' : [],
    'Columbus Blue Jackets' : [],
    'Dallas Stars' : [],
    'Detroit Red Wings' : [],
    'Edmonton Oilers' : [],
    'Florida Panthers' : [],
    'Los Angeles Kings' : [],
    'Minnesota Wild' : [],
    'Montreal Canadiens' : [],
    'Nashville Predators' : [],
    'New Jersey Devils' : [],
    'New York Islanders' : [],
    'New York Rangers' : [],
    'Ottawa Senators' : [],
    'Philadelphia Flyers' : [],
    'Pittsburgh Penguins' : [],
    'San Jose Sharks' : [],
    'Seattle Kraken' : [],
    'St. Louis Blues' : [],
    'Tampa Bay Lightning' : [],
    'Toronto Maple Leafs' : [],
    'Vancouver Canucks' : [],
    'Vegas Golden Knights' : [],
    'Washington Capitals' : [],
    'Winnipeg Jets' : [],
}

ranking_dates = []

def average_rankings_parse(file_name : str = "") -> None:
    header_row = True

    # open the average rating file
    with open(file_name, newline='') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for rating in ratings:
            if header_row:
                header_row = False
                continue

            if len(rating) == 0:
                continue
            
            # take the ranking and extract the date
            date = rating[0].split("/")
            date[2] = date[2].split(" ")
            date = datetime.date(int(date[2][0]), int(date[1]), int(date[0]))

            # if we have not seen this date then add it do the ranking data list
            if ranking_dates.count(date) == 0:
                ranking_dates.append(date)

            # special case for the canadians french spelling
            if rating[1] == 'MontrÃ©al Canadiens':
                ranking_averages['Montreal Canadiens'].append(float(rating[3]))
                continue

            # for every team, add the rating for that week
            ranking_averages[rating[1]].append(float(rating[3]))


def average_rankings_update(total_ratings : dict = {},
                            average_rankings : dict = {}) -> None:
    tuple_list = []
    for team, rating in total_ratings.items():
        tuple_list.append(tuple((team, rating)))
    tuple_list.sort(key = lambda x: x[1], reverse=True)

    # print("Before")
    # for team in ranking_averages.keys():
    #     print("{} : {}".format(team, ranking_averages[team]))
    # print()

    for count in range(1, len(tuple_list)+1, 1):
        sum = 0
        team = tuple_list[count-1][0]
        for rank in average_rankings[team]:
            sum += rank
        sum /= len(average_rankings[team])
        ranking_averages[team].append(sum)

    # print("After")
    # for team in ranking_averages.keys():
    #     print("{} : {}".format(team, ranking_averages[team]))
    # print()


def average_rankings_write_out() -> None:
    date = str(datetime.datetime.now())
    date_split = date.split(" ")
    date_split = date_split[0].split("-")

    # get the current date and version for that column
    date_rating = date_split[2] + "/" + date_split[1] + "/" + date_split[0] + \
        " (v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + ")"

    print(ranking_averages)
    with open("Input_Files/AverageRankings.csv", 'a', newline='') as csv_date_file:
        csv_writer = csv.writer(csv_date_file, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)

        # for each team print the rating with this timestamp
        for team in ranking_averages.keys():
            csv_writer.writerow([date_rating, team, divisions[team],
                int(ranking_averages[team][len(ranking_averages[team])-1])])


if __name__ == "__main__":
    average_rankings_parse("Input_Files/AverageRankings.csv")
    for date in ranking_dates:
        print(date)
    for team in ranking_averages.keys():
        print("{}: {}".format(team, ranking_averages[team]))
