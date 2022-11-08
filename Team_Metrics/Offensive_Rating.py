import requests
import json
from enum import Enum

offensive_rating = {
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


class offensive_rating_weights(Enum):
    POWER_PLAY_STRENGTH = 0.20
    GOALS_PER_GAME = 0.50
    SHOTS_PER_GAME = 0.30


def offensive_rating_get_dict() -> dict:
    return offensive_rating


def offensive_rating_get_data_set() -> list:
    # Get the top level record from the API
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    # place the requried data into a dictionary for later use
    shooting_data = {}
    goal_data = {}
    power_play = {}
    for team in parsed_data["teams"]:
        team_name = team["teamStats"][0]["splits"][0]["team"]["name"]
        SPG = team["teamStats"][0]["splits"][0]["stat"]["shotsPerGame"]
        GPG = team["teamStats"][0]["splits"][0]["stat"]["goalsPerGame"]
        PPP = float(
            team["teamStats"][0]["splits"][0]["stat"]["powerPlayPercentage"])
        shooting_data[team_name] = SPG
        goal_data[team_name] = GPG
        power_play[team_name] = PPP
    return [shooting_data, goal_data, power_play]


def offensive_rating_combine_metrics(metric_list : list=[]) -> None:
    for team in offensive_rating.keys():
        offensive_rating[team] = \
            (metric_list[0][team] * \
                offensive_rating_weights.SHOTS_PER_GAME.value) + \
            (metric_list[1][team] * \
                offensive_rating_weights.GOALS_PER_GAME.value) + \
            (metric_list[2][team] * \
                offensive_rating_weights.POWER_PLAY_STRENGTH.value)


if __name__ == "__main__":
    offensive_metrics = offensive_rating_get_data_set()
    offensive_rating_combine_metrics(offensive_metrics)
    for team in offensive_rating.keys():
        print()