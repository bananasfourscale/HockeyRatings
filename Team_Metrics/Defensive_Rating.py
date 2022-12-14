from enum import Enum


defensive_rating = {
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


class defensive_rating_weights(Enum):
    PENALTY_KILL_STRENGTH = 0.20
    GOALS_AGAINST_PER_GAME = 0.50
    SHOTS_AGAINST_PER_GAME = 0.30


def defensive_rating_get_dict() -> dict:
    return defensive_rating


def defensive_rating_get_data_set(team_stats : dict={}) -> list:

    # place the requried data into a dictionary for later use
    shooting_data = {}
    goal_against_data = {}
    penalty_kill_data = {}
    for team in team_stats.keys():
        shooting_data[team] = team_stats[team]["shotsAllowed"]
        goal_against_data[team] = team_stats[team]["goalsAgainstPerGame"]
        penalty_kill_data[team] = \
            float(team_stats[team]["penaltyKillPercentage"])
    return [shooting_data, goal_against_data, penalty_kill_data]


def defensive_rating_combine_metrics(metric_list : list=[]) -> None:
    for team in defensive_rating.keys():
        defensive_rating[team] = \
            (metric_list[0][team] * \
                defensive_rating_weights.SHOTS_AGAINST_PER_GAME.value) + \
            (metric_list[1][team] * \
                defensive_rating_weights.GOALS_AGAINST_PER_GAME.value) + \
            (metric_list[2][team] * \
                defensive_rating_weights.PENALTY_KILL_STRENGTH.value)
