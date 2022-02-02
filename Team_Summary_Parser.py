import csv
from asyncio.windows_events import NULL
from enum import *

team_summary_data = {
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

class summary_indecies(Enum):
    TEAM = 0
    SEASON = 1
    GAMES_PLAYED = 2

def parse_team_summary(file_name : str = "") -> None:
    current_rating = 0
    with open(file_name, newline='') as csv_data_file:
        summaries = csv.reader(csv_data_file, delimiter = ',')
        for summary in summaries:
            if current_rating == 1:
                team_summary_data['Anaheim Ducks'] = summary

            if current_rating == 2:
                team_summary_data['Arizona Coyotes'] = summary
                
            if current_rating == 3:
                team_summary_data['Boston Bruins'] = summary
                
            if current_rating == 4:
                team_summary_data['Buffalo Sabres'] = summary
                
            if current_rating == 5:
                team_summary_data['Calgary Flames'] = summary
                
            if current_rating == 6:
                team_summary_data['Carolina Hurricanes'] = summary
                
            if current_rating == 7:
                team_summary_data['Chicago Blackhawks'] = summary
                
            if current_rating == 8:
                team_summary_data['Colorado Avalanche'] = summary
                
            if current_rating == 9:
                team_summary_data['Columbus Blue Jackets'] = summary
                
            if current_rating == 10:
                team_summary_data['Dallas Stars'] = summary
                
            if current_rating == 11:
                team_summary_data['Detroit Red Wings'] = summary
                
            if current_rating == 12:
                team_summary_data['Edmonton Oilers'] = summary
                
            if current_rating == 13:
                team_summary_data['Florida Panthers'] = summary
                
            if current_rating == 14:
                team_summary_data['Los Angeles Kings'] = summary
                
            if current_rating == 15:
                team_summary_data['Minnesota Wild'] = summary
                
            if current_rating == 16:
                team_summary_data['Montreal Canadiens'] = summary
                
            if current_rating == 17:
                team_summary_data['Nashville Predators'] = summary
                
            if current_rating == 18:
                team_summary_data['New Jersey Devils'] = summary
                
            if current_rating == 19:
                team_summary_data['New York Islanders'] = summary
                
            if current_rating == 20:
                team_summary_data['New York Rangers'] = summary
                
            if current_rating == 21:
                team_summary_data['Ottawa Senators'] = summary
                
            if current_rating == 22:
                team_summary_data['Philadelphia Flyers'] = summary
                
            if current_rating == 23:
                team_summary_data['Pittsburgh Penguins'] = summary
                
            if current_rating == 24:
                team_summary_data['San Jose Sharks'] = summary
                
            if current_rating == 25:
                team_summary_data['Seattle Kraken'] = summary
                
            if current_rating == 26:
                team_summary_data['St. Louis Blues'] = summary
                
            if current_rating == 27:
                team_summary_data['Tampa Bay Lightning'] = summary
                
            if current_rating == 28:
                team_summary_data['Toronto Maple Leafs'] = summary
                
            if current_rating == 29:
                team_summary_data['Vancouver Canucks'] = summary
                
            if current_rating == 30:
                team_summary_data['Vegas Golden Knights'] = summary
                
            if current_rating == 31:
                team_summary_data['Washington Capitals'] = summary
                
            if current_rating == 32:
                team_summary_data['Winnipeg Jets'] = summary
            
            current_rating += 1

if __name__ == "__main__":
    parse_team_summary("Input_Files/TeamSummary.csv")
    print(team_summary_data)
