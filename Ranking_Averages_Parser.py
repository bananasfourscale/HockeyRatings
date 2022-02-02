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

average_ratings_header = []

def parse_average_ratings(file_name : str = "") -> None:
    current_rating = 0
    empty_columns = 0

    # open the average rating file
    with open(file_name, newline='') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = '\t')

        # loop through the lines of file
        for rating in ratings:

            # remove all empty comlumns
            empty_columns = rating.count('')
            while empty_columns > 0:
                rating.remove('')
                empty_columns -= 1
            
            if current_rating == 0:
                average_ratings_header.extend(rating)

            if current_rating == 1:
                ranking_averages['Anaheim Ducks'] = rating

            if current_rating == 2:
                ranking_averages['Arizona Coyotes'] = rating
                
            if current_rating == 3:
                ranking_averages['Boston Bruins'] = rating
                
            if current_rating == 4:
                ranking_averages['Buffalo Sabres'] = rating
                
            if current_rating == 5:
                ranking_averages['Calgary Flames'] = rating
                
            if current_rating == 6:
                ranking_averages['Carolina Hurricanes'] = rating
                
            if current_rating == 7:
                ranking_averages['Chicago Blackhawks'] = rating
                
            if current_rating == 8:
                ranking_averages['Colorado Avalanche'] = rating
                
            if current_rating == 9:
                ranking_averages['Columbus Blue Jackets'] = rating
                
            if current_rating == 10:
                ranking_averages['Dallas Stars'] = rating
                
            if current_rating == 11:
                ranking_averages['Detroit Red Wings'] = rating
                
            if current_rating == 12:
                ranking_averages['Edmonton Oilers'] = rating
                
            if current_rating == 13:
                ranking_averages['Florida Panthers'] = rating
                
            if current_rating == 14:
                ranking_averages['Los Angeles Kings'] = rating
                
            if current_rating == 15:
                ranking_averages['Minnesota Wild'] = rating
                
            if current_rating == 16:
                ranking_averages['Montreal Canadiens'] = rating
                
            if current_rating == 17:
                ranking_averages['Nashville Predators'] = rating
                
            if current_rating == 18:
                ranking_averages['New Jersey Devils'] = rating
                
            if current_rating == 19:
                ranking_averages['New York Islanders'] = rating
                
            if current_rating == 20:
                ranking_averages['New York Rangers'] = rating
                
            if current_rating == 21:
                ranking_averages['Ottawa Senators'] = rating
                
            if current_rating == 22:
                ranking_averages['Philadelphia Flyers'] = rating
                
            if current_rating == 23:
                ranking_averages['Pittsburgh Penguins'] = rating
                
            if current_rating == 24:
                ranking_averages['San Jose Sharks'] = rating
                
            if current_rating == 25:
                ranking_averages['Seattle Kraken'] = rating
                
            if current_rating == 26:
                ranking_averages['St. Louis Blues'] = rating
                
            if current_rating == 27:
                ranking_averages['Tampa Bay Lightning'] = rating
                
            if current_rating == 28:
                ranking_averages['Toronto Maple Leafs'] = rating
                
            if current_rating == 29:
                ranking_averages['Vancouver Canucks'] = rating
                
            if current_rating == 30:
                ranking_averages['Vegas Golden Knights'] = rating
                
            if current_rating == 31:
                ranking_averages['Washington Capitals'] = rating
                
            if current_rating == 32:
                ranking_averages['Winnipeg Jets'] = rating
            
            current_rating += 1
        # print(ranking_averages)
        # print(average_ratings_header)


def parse_average_rating_header_row(header_row : list = []) -> None:
    if len(header_row) == 0:
        return
    for column in header_row:
        if column == 'Team':
            continue
        if column == 'N/A':
            continue
        header_line = column.split(" ")
        date = header_line[0].split("/")
        ranking_dates.append(datetime.date(int(date[2]), int(date[1]),
            int(date[0])))
    #print(ranking_dates)


if __name__ == "__main__":
    parse_average_ratings("Input_Files/AverageRatings.csv")
    parse_average_rating_header_row(average_ratings_header)
