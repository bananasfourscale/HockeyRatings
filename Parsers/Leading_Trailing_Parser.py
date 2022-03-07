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
    # SEASON = 1
    GP = 1
    PTS_PER = 2
    GF_P1 = 3
    GA_P1 = 4
    GF_P2 = 5
    GA_P2 = 6
    W_LEAD_1 = 7
    L_LEAD_1 = 8
    T_LEAD_1 = 9
    OT_LEAD_1 = 10
    W_PER_LEAD_1 = 11
    W_LEAD_2 = 12
    L_LEAD_2 = 13
    T_LEAD_2 = 14
    OT_LEAD_2 = 15
    W_PER_LEAD_2 = 16
    W_TRAIL_1 = 17
    L_TRAIL_1 = 18
    T_TRAIL_1 = 19
    OT_TRAIL_1 = 20
    W_PER_TRAIL_1 = 21
    W_TRAIL_2 = 22
    L_TRAIL_2 = 23
    T_TRAIL_2 = 24
    OT_TRAIL_2 = 25
    W_PER_TRAIL_2 = 26


def parse_leading_trailing(file_name : str = "") -> None:
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
            if summary[leading_trailing_indecies.TEAM.value] == \
                'MontÃ©al Canadiens':
                leading_trailing_data['Montreal Canadiens'] = summary
                continue

            # use the team name to sort the row data into the dictionary
            leading_trailing_data[summary[
                leading_trailing_indecies.TEAM.value]] = summary


if __name__ == "__main__":
    parse_leading_trailing("Input_Files/LeadingTrailing.csv")
    print(leading_trailing_data)
