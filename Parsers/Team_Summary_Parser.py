import csv
from enum import Enum
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup

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
    SEASON = 4
    GP = 8
    W = 11
    L = 14
    T = 17
    OT = 20
    PTS = 23
    PTS_PER = 26
    RW = 29
    ROW = 32
    SOW = 35
    GF = 38
    GA = 41
    GF_GP = 44
    GA_GP = 47
    PP_PER = 50
    PK_PER = 53
    NET_PP = 56
    NET_PK = 59
    SHF_GP = 62
    SHA_GP = 65
    FOW_PER = 68


def scrap_team_summary() -> dict:
    driver = webdriver.Chrome("P:\\chromedriver.exe")
    driver.get("https://www.nhl.com/stats/teams")
    sleep(10)
    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource, 'html.parser')
    driver.close()
    source_str = soup.prettify()
    table_index = source_str.find(
        '''<div class="rt-tbody" role="rowgroup" style="min-width: 1244px;">''')
    source_str_trimmed = source_str[table_index:-1]
    table_index = source_str_trimmed.find(
        '''<button class="prev-button" disabled="">''')
    source_str_trimmed = source_str_trimmed[0:table_index]
    source_str_trimmed = source_str_trimmed.split('\n')
    index = 0
    for row in source_str_trimmed:
        if row.strip() in team_summary_data.keys():
            print(row)
    del source_str_trimmed
    del source_str
    del soup
    del pageSource
    del driver

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
    # parse_team_summary("Input_Files/TeamSummary.csv")
    # print(team_summary_data)
    scrap_team_summary()
