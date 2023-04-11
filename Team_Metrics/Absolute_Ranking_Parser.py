import csv

ranking_absolutes = {
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


def absolute_rankings_get_dict() -> dict:
    return ranking_absolutes


def absolute_rankings_parse(file_name : str = "") -> None:
    header_row = True

    # open the average rating file
    with open(file_name, newline='', encoding='utf-16') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for rating in ratings:
            if header_row:
                header_row = False
                continue

            if len(rating) == 0:
                continue

            # special case for the canadians french spelling
            if rating[1] == 'MontrÃ©al Canadiens':
                ranking_absolutes['Montréal Canadiens'].append(float(rating[3]))
                continue

            # for every team, add the rating for that week
            ranking_absolutes[rating[1]].append(float(rating[3]))


def absolute_rankings_update(total_ratings : dict = {}) -> None:
    tuple_list = []
    for team, rating in total_ratings.items():
        tuple_list.append(tuple((team, rating)))
    tuple_list.sort(key = lambda x: x[1], reverse=True)

    for count in range(1, len(tuple_list)+1, 1):
        team = tuple_list[count-1][0]
        ranking_absolutes[team].append(float(count))


if __name__ == "__main__":
    absolute_rankings_parse("Trend_Files/AbsoluteRankings.csv")
    for team in ranking_absolutes.keys():
        print("{}: {}".format(team, ranking_absolutes[team]))
