import csv
from enum import Enum

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
    GP = 2
    W = 3
    L = 4
    T = 5
    OT = 6
    PTS = 7
    PTS_PER = 8
    RW = 9
    ROW = 10
    SOW = 11
    GF = 12
    GA = 13
    GF_GP = 14
    GA_GP = 15
    PP_PER = 16
    PK_PER = 17
    NET_PP = 18
    NET_PK = 19
    SHF_GP = 20
    SHA_GP = 21
    FOW_PER = 22


def parse_team_summary(file_name : str = "") -> None:
    header_row = True
    with open(file_name, newline='') as csv_data_file:
        summaries = csv.reader(csv_data_file, delimiter = ',')

        # loop through all rows of the file
        for summary in summaries:

            # always skip the header row
            if header_row == True:
                header_row = False
                continue

            # special case for the Habs french spelling
            if summary[summary_indecies.TEAM.value] == 'MontÃ©al Canadiens':
                team_summary_data['Montreal Canadiens'] = summary
                continue

            # use the team name to sort the row data into the dictionary
            team_summary_data[summary[summary_indecies.TEAM.value]] = summary


if __name__ == "__main__":
    parse_team_summary("Input_Files/TeamSummary.csv")
    print(team_summary_data)
