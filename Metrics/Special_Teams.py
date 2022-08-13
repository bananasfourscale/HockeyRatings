from math import exp
import requests
import json
from numpy import std, var, mean

special_teams = {
    'Anaheim Ducks' : 0,
    'Arizona Coyotes' : 0,
    'Boston Bruins' : 0,
    'Buffalo Sabres' : 0,
    'Calgary Flames' : 0,
    'Carolina Hurricanes' : 0,
    'Chicago Blackhawks' : 0,
    'Colorado Avalanche' : 0,
    'Columbus Blue Jackets' : 0,
    'Dallas Stars' : 0,
    'Detroit Red Wings' : 0,
    'Edmonton Oilers' : 0,
    'Florida Panthers' : 0,
    'Los Angeles Kings' : 0,
    'Minnesota Wild' : 0,
    'Montréal Canadiens' : 0,
    'Nashville Predators' : 0,
    'New Jersey Devils' : 0,
    'New York Islanders' : 0,
    'New York Rangers' : 0,
    'Ottawa Senators' : 0,
    'Philadelphia Flyers' : 0,
    'Pittsburgh Penguins' : 0,
    'San Jose Sharks' : 0,
    'Seattle Kraken' : 0,
    'St. Louis Blues' : 0,
    'Tampa Bay Lightning' : 0,
    'Toronto Maple Leafs' : 0,
    'Vancouver Canucks' : 0,
    'Vegas Golden Knights' : 0,
    'Washington Capitals' : 0,
    'Winnipeg Jets' : 0,
}


def special_teams_get_data() -> dict:
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    special_teams_data = {}
    parsed_data = json.loads(web_data.content)
    for team in parsed_data["teams"]:
        PPper = team["teamStats"][0]["splits"][0]["stat"]["powerPlayPercentage"]
        PKper = \
            team["teamStats"][0]["splits"][0]["stat"]["penaltyKillPercentage"]
        special_teams_data[
            team["teamStats"][0]["splits"][0]["team"]["name"]] = [PPper, PKper]
    return special_teams_data            


def special_teams_combine() -> None:
    special_teams_data = special_teams_get_data()
    for team in special_teams_data.keys():
        net_pp = float(special_teams_data[team][0])
        net_pk = float(special_teams_data[team][1])
        special_teams[team] = net_pp + net_pk


def special_teams_apply_sigmoid() -> None:
    for team in special_teams.keys():
        special_teams[team] = \
            1/(1 + exp(-(0.23 * (special_teams[team] - 100))))


if __name__ == "__main__":
    special_teams_combine()
    print("Special Teams Ratings:")
    for team in special_teams.keys():
        print("\t" + team + '=' + str(special_teams[team]))
    special_teams_apply_sigmoid()
    print("Special Teams Ratings:")
    for team in special_teams.keys():
        print("\t" + team + '=' + str(special_teams[team]))
