import csv
from enum import Enum

last_ten_data = {
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

class last_ten_indecies(Enum):
    TEAM = 0
    LAST_TEN = 1


def parse_last_ten(file_name : str = "") -> None:
    current_rating = 0
    with open(file_name, newline='') as csv_data_file:
        summaries = csv.reader(csv_data_file, delimiter = ',')
        for summary in summaries:
            if current_rating == 1:
                last_ten_data['Anaheim Ducks'] = summary

            if current_rating == 2:
                last_ten_data['Arizona Coyotes'] = summary
                
            if current_rating == 3:
                last_ten_data['Boston Bruins'] = summary
                
            if current_rating == 4:
                last_ten_data['Buffalo Sabres'] = summary
                
            if current_rating == 5:
                last_ten_data['Calgary Flames'] = summary
                
            if current_rating == 6:
                last_ten_data['Carolina Hurricanes'] = summary
                
            if current_rating == 7:
                last_ten_data['Chicago Blackhawks'] = summary
                
            if current_rating == 8:
                last_ten_data['Colorado Avalanche'] = summary
                
            if current_rating == 9:
                last_ten_data['Columbus Blue Jackets'] = summary
                
            if current_rating == 10:
                last_ten_data['Dallas Stars'] = summary
                
            if current_rating == 11:
                last_ten_data['Detroit Red Wings'] = summary
                
            if current_rating == 12:
                last_ten_data['Edmonton Oilers'] = summary
                
            if current_rating == 13:
                last_ten_data['Florida Panthers'] = summary
                
            if current_rating == 14:
                last_ten_data['Los Angeles Kings'] = summary
                
            if current_rating == 15:
                last_ten_data['Minnesota Wild'] = summary
                
            if current_rating == 16:
                last_ten_data['Montreal Canadiens'] = summary
                
            if current_rating == 17:
                last_ten_data['Nashville Predators'] = summary
                
            if current_rating == 18:
                last_ten_data['New Jersey Devils'] = summary
                
            if current_rating == 19:
                last_ten_data['New York Islanders'] = summary
                
            if current_rating == 20:
                last_ten_data['New York Rangers'] = summary
                
            if current_rating == 21:
                last_ten_data['Ottawa Senators'] = summary
                
            if current_rating == 22:
                last_ten_data['Philadelphia Flyers'] = summary
                
            if current_rating == 23:
                last_ten_data['Pittsburgh Penguins'] = summary
                
            if current_rating == 24:
                last_ten_data['San Jose Sharks'] = summary
                
            if current_rating == 25:
                last_ten_data['Seattle Kraken'] = summary
                
            if current_rating == 26:
                last_ten_data['St. Louis Blues'] = summary
                
            if current_rating == 27:
                last_ten_data['Tampa Bay Lightning'] = summary
                
            if current_rating == 28:
                last_ten_data['Toronto Maple Leafs'] = summary
                
            if current_rating == 29:
                last_ten_data['Vancouver Canucks'] = summary
                
            if current_rating == 30:
                last_ten_data['Vegas Golden Knights'] = summary
                
            if current_rating == 31:
                last_ten_data['Washington Capitals'] = summary
                
            if current_rating == 32:
                last_ten_data['Winnipeg Jets'] = summary
            
            current_rating += 1


if __name__ == "__main__":
    parse_last_ten("Input_Files/Last10Games.csv")
    print(last_ten_data)
