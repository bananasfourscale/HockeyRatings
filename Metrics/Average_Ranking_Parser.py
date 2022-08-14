import csv
import datetime

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
    'Montréal Canadiens' : [],
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


def average_rankings_get_dict() -> dict:
    return ranking_averages


def average_ranking_get_ranking_dates() -> list:
    return ranking_dates


def average_rankings_parse(file_name : str = "") -> None:
    header_row = True

    # open the average rating file
    with open(file_name, newline='', encoding='utf-8') as csv_data_file:
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

            # for every team, add the rating for that week
            ranking_averages[rating[1]].append(float(rating[3]))


def average_rankings_update(total_ratings : dict = {},
                            average_rankings : dict = {}) -> None:
    tuple_list = []
    for team, rating in total_ratings.items():
        tuple_list.append(tuple((team, rating)))
    tuple_list.sort(key = lambda x: x[1], reverse=True)
    for count in range(1, len(tuple_list)+1, 1):
        sum = 0
        team = tuple_list[count-1][0]
        for rank in average_rankings[team]:
            sum += rank
        sum /= len(average_rankings[team])
        ranking_averages[team].append(sum)


if __name__ == "__main__":
    average_rankings_parse('Output_Files/Trend_Files/AverageRankings.csv')
    for date in ranking_dates:
        print(date)
    for team in ranking_averages.keys():
        print("{}: {}".format(team, ranking_averages[team]))
