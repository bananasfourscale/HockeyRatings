import csv
from enum import Enum

leading_trailing_data = {
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

class leading_trailing_indecies(Enum):
    TEAM = 0
    SEASON = 1
    GP = 2
    PTS_PER = 3
    GF_P1 = 4
    GA_P1 = 5
    GF_P2 = 6
    GA_P2 = 7
    W_LEAD_1 = 8
    L_LEAD_1 = 9
    T_LEAD_1 = 10
    OT_LEAD_1 = 11
    W_PER_LEAD_1 = 12
    W_LEAD_2 = 13
    L_LEAD_2 = 14
    T_LEAD_2 = 15
    OT_LEAD_2 = 16
    W_PER_LEAD_2 = 17
    W_TRAIL_1 = 18
    L_TRAIL_1 = 19
    T_TRAIL_1 = 20
    OT_TRAIL_1 = 21
    W_PER_TRAIL_1 = 22
    W_TRAIL_2 = 23
    L_TRAIL_2 = 24
    T_TRAIL_2 = 25
    OT_TRAIL_2 = 26
    W_PER_TRAIL_2 = 27


def parse_leading_trailing(file_name : str = "") -> None:
    current_rating = 0
    with open(file_name, newline='') as csv_data_file:
        summaries = csv.reader(csv_data_file, delimiter = ',')
        for summary in summaries:
            if current_rating == 1:
                leading_trailing_data['Anaheim Ducks'] = summary

            if current_rating == 2:
                leading_trailing_data['Arizona Coyotes'] = summary
                
            if current_rating == 3:
                leading_trailing_data['Boston Bruins'] = summary
                
            if current_rating == 4:
                leading_trailing_data['Buffalo Sabres'] = summary
                
            if current_rating == 5:
                leading_trailing_data['Calgary Flames'] = summary
                
            if current_rating == 6:
                leading_trailing_data['Carolina Hurricanes'] = summary
                
            if current_rating == 7:
                leading_trailing_data['Chicago Blackhawks'] = summary
                
            if current_rating == 8:
                leading_trailing_data['Colorado Avalanche'] = summary
                
            if current_rating == 9:
                leading_trailing_data['Columbus Blue Jackets'] = summary
                
            if current_rating == 10:
                leading_trailing_data['Dallas Stars'] = summary
                
            if current_rating == 11:
                leading_trailing_data['Detroit Red Wings'] = summary
                
            if current_rating == 12:
                leading_trailing_data['Edmonton Oilers'] = summary
                
            if current_rating == 13:
                leading_trailing_data['Florida Panthers'] = summary
                
            if current_rating == 14:
                leading_trailing_data['Los Angeles Kings'] = summary
                
            if current_rating == 15:
                leading_trailing_data['Minnesota Wild'] = summary
                
            if current_rating == 16:
                leading_trailing_data['Montreal Canadiens'] = summary
                
            if current_rating == 17:
                leading_trailing_data['Nashville Predators'] = summary
                
            if current_rating == 18:
                leading_trailing_data['New Jersey Devils'] = summary
                
            if current_rating == 19:
                leading_trailing_data['New York Islanders'] = summary
                
            if current_rating == 20:
                leading_trailing_data['New York Rangers'] = summary
                
            if current_rating == 21:
                leading_trailing_data['Ottawa Senators'] = summary
                
            if current_rating == 22:
                leading_trailing_data['Philadelphia Flyers'] = summary
                
            if current_rating == 23:
                leading_trailing_data['Pittsburgh Penguins'] = summary
                
            if current_rating == 24:
                leading_trailing_data['San Jose Sharks'] = summary
                
            if current_rating == 25:
                leading_trailing_data['Seattle Kraken'] = summary
                
            if current_rating == 26:
                leading_trailing_data['St. Louis Blues'] = summary
                
            if current_rating == 27:
                leading_trailing_data['Tampa Bay Lightning'] = summary
                
            if current_rating == 28:
                leading_trailing_data['Toronto Maple Leafs'] = summary
                
            if current_rating == 29:
                leading_trailing_data['Vancouver Canucks'] = summary
                
            if current_rating == 30:
                leading_trailing_data['Vegas Golden Knights'] = summary
                
            if current_rating == 31:
                leading_trailing_data['Washington Capitals'] = summary
                
            if current_rating == 32:
                leading_trailing_data['Winnipeg Jets'] = summary
            
            current_rating += 1


if __name__ == "__main__":
    parse_leading_trailing("Input_Files/LeadingTrailing.csv")
    print(leading_trailing_data)
