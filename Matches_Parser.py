import csv
from enum import Enum

matches = []

class match_indecies(Enum):
    DATE = 0
    AWAY_TEAM = 1
    AWAY_SCORE = 2
    HOME_TEAM = 3
    HOME_SCORE = 4
    EXTRA_TIME = 5
    ATTENDANCE = 6
    GAME_LENGTH = 7
    NOTES = 8

def parse_matches(file_name : str = "") -> None:
    header_row = True
    with open(file_name, newline='') as csv_data_file:
        match_list = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for game in match_list:
            if header_row :
                header_row = False
                continue
            matches.append(game)
