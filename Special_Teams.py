from Team_Summary_Parser import *
import math

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
    'Montreal Canadiens' : 0,
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


def special_teams_combine() -> None:
    for team in special_teams.keys():
        net_pp = float(team_summary_data[team][summary_indecies.NET_PP.value])
        net_pk = float(team_summary_data[team][summary_indecies.NET_PK.value])
        special_teams[team] = net_pp + net_pk


def special_teams_apply_sigmoid() -> None:
    for team in special_teams.keys():
        special_teams[team] = \
            1/(1 + math.exp(-(0.23 * (special_teams[team] - 100))))


if __name__ == "__main__":
    parse_team_summary('Input_Files/TeamSummary.csv')
    special_teams_combine()
    special_teams_apply_sigmoid()
