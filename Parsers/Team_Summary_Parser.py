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

class trimmed_html_rows(Enum):
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

def scrap_team_summary() -> None:
    driver = webdriver.Chrome("C:\\Users\\lindb\\Documents\\chromedriver_win32\\chromedriver.exe")
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
    while index < len(source_str_trimmed):
        if source_str_trimmed[index].strip() in team_summary_data.keys():
            source_str_trimmed[index].strip()
            team_summary_data[source_str_trimmed[index].strip()].append([
                source_str_trimmed[index + trimmed_html_rows.SEASON.value],
                source_str_trimmed[index + trimmed_html_rows.GP.value],
                source_str_trimmed[index + trimmed_html_rows.W.value],
                source_str_trimmed[index + trimmed_html_rows.L.value],
                source_str_trimmed[index + trimmed_html_rows.SEASON.value],
                source_str_trimmed[index + trimmed_html_rows.T.value],
                source_str_trimmed[index + trimmed_html_rows.OT.value],
                source_str_trimmed[index + trimmed_html_rows.PTS.value],
                source_str_trimmed[index + trimmed_html_rows.PTS_PER.value],
                source_str_trimmed[index + trimmed_html_rows.RW.value],
                source_str_trimmed[index + trimmed_html_rows.ROW.value],
                source_str_trimmed[index + trimmed_html_rows.SOW.value],
                source_str_trimmed[index + trimmed_html_rows.GF.value],
                source_str_trimmed[index + trimmed_html_rows.GA.value],
                source_str_trimmed[index + trimmed_html_rows.GF_GP.value],
                source_str_trimmed[index + trimmed_html_rows.GA_GP.value],
                source_str_trimmed[index + trimmed_html_rows.PP_PER.value],
                source_str_trimmed[index + trimmed_html_rows.PK_PER.value],
                source_str_trimmed[index + trimmed_html_rows.NET_PP.value],
                source_str_trimmed[index + trimmed_html_rows.NET_PK.value],
                source_str_trimmed[index + trimmed_html_rows.SHF_GP.value],
                source_str_trimmed[index + trimmed_html_rows.SHA_GP.value],
                source_str_trimmed[index + trimmed_html_rows.FOW_PER.value]])
            index += trimmed_html_rows.FOW_PER.value
        else:
            index += 1


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

            team_summary_data[summary[trimmed_html_rows.TEAM.value]] = summary


if __name__ == "__main__":
    # parse_team_summary("Input_Files/TeamSummary.csv")
    # print(team_summary_data)
    scrap_team_summary()
    print(team_summary_data)
