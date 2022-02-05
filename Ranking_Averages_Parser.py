import csv
import datetime
from asyncio.windows_events import NULL

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

def parse_average_ratings(file_name : str = "") -> None:
    header_row = True

    # open the average rating file
    with open(file_name, newline='') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for rating in ratings:
            if header_row:
                header_row = False
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


if __name__ == "__main__":
    parse_average_ratings("Input_Files/AverageRatings.csv")
    for date in ranking_dates:
        print(date)
    for team in ranking_averages.keys():
        print("{}: {}".format(team, ranking_averages[team]))
