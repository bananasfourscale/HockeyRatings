import requests
import json
from math import exp

scoring_difference = {
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

shooting_difference = {
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

scoring_rating = {
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

def scoring_diff_get_data() -> dict:
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    scoring_diff_data = {}
    parsed_data = json.loads(web_data.content)
    for team in parsed_data["teams"]:
        GPG = team["teamStats"][0]["splits"][0]["stat"]["goalsPerGame"]
        GAPG = team["teamStats"][0]["splits"][0]["stat"]["goalsAgainstPerGame"]
        scoring_diff_data[
            team["teamStats"][0]["splits"][0]["team"]["name"]] = [GPG, GAPG]
    return scoring_diff_data 


def scoring_rating_calc_goal_diff() -> None:
    scoring_diff_data = scoring_diff_get_data()
    for team in scoring_diff_data.keys():

        # reassign the data values just to make it easier to use
        goals_for = float(scoring_diff_data[team][0])
        goals_against = float(scoring_diff_data[team][1])

        # calculate scoring diff
        scoring_difference[team] = goals_for - goals_against
        # print("{} : {}".format(team, scoring_difference[team]))


def scoring_rating_apply_sigmoid_goal_diff() -> None:
    for team in scoring_difference.keys():
        scoring_difference[team] = \
            1/(1 + exp(-(2.3 * (scoring_difference[team]))))
        # print("{} : {}".format(team, scoring_difference[team]))


def shooting_diff_get_data() -> dict:
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    scoring_diff_data = {}
    parsed_data = json.loads(web_data.content)
    for team in parsed_data["teams"]:
        SPG = team["teamStats"][0]["splits"][0]["stat"]["shotsPerGame"]
        SAPG = team["teamStats"][0]["splits"][0]["stat"]["shotsAllowed"]
        scoring_diff_data[
            team["teamStats"][0]["splits"][0]["team"]["name"]] = [SPG, SAPG]
    return scoring_diff_data


def scoring_rating_calc_shooting_diff() -> None:
    shooting_diff_data = shooting_diff_get_data()
    for team in shooting_diff_data.keys():

        # reassign the data values just to make it easier to use
        goals_for = float(shooting_diff_data[team][0])
        goals_against = float(shooting_diff_data[team][1])

        # calculate scoring diff
        shooting_difference[team] = goals_for - goals_against
        # print("{} : {}".format(team, shooting_difference[team]))


def scoring_rating_apply_sigmoid_shooting_diff() -> None:
    for team in shooting_difference.keys():
        shooting_difference[team] = \
            1/(1 + exp(-(0.46 * (shooting_difference[team]))))
        # print("{} : {}".format(team, shooting_difference[team]))


def scoring_rating_combine_factors() -> None:
    for team in scoring_rating.keys():
        scoring_rating[team] = (scoring_difference[team] * 0.75) + \
            (shooting_difference[team] * 0.25)

if __name__ == "__main__":
    scoring_rating_calc_goal_diff()
    scoring_rating_apply_sigmoid_goal_diff()
    print("Scoring Diff:")
    for team in scoring_difference.keys():
        print("\t" + team + '=' + str(scoring_difference[team]))
    scoring_rating_calc_shooting_diff()
    scoring_rating_apply_sigmoid_shooting_diff()
    print("Shooting Diff:")
    for team in shooting_difference.keys():
        print("\t" + team + '=' + str(shooting_difference[team]))
    scoring_rating_combine_factors()
    print("Combined Scoring Rating:")
    for team in scoring_rating.keys():
        print("\t" + team + '=' + str(scoring_rating[team]))
