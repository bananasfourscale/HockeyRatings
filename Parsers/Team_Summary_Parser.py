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
    # SEASON = 1
    GP = 1
    W = 2
    L = 3
    T = 4
    OT = 5
    PTS = 6
    PTS_PER = 7
    RW = 8
    ROW = 9
    SOW = 10
    GF = 11
    GA = 12
    GF_GP = 13
    GA_GP = 14
    PP_PER = 15
    PK_PER = 16
    NET_PP = 17
    NET_PK = 18
    SHF_GP = 19
    SHA_GP = 20
    FOW_PER = 21


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
            else:
                team_summary_data[summary[summary_indecies.TEAM.value]] = summary


if __name__ == "__main__":
    parse_team_summary("Input_Files/TeamSummary.csv")
    print(team_summary_data)
