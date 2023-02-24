from enum import Enum
import datetime
import csv

strength_of_schedule = {
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

strength_of_schedule_games_played = {
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


strength_of_schedule_trends = {
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

class strength_of_schedule_weights(Enum):
    WIN_REGULATION_WEIGHT = 1.0
    LOSE_REGULATION_WEIGHT = 0.0
    WIN_OT_WEIGHT = 0.33
    LOSE_OT_WEIGHT = 0.10
    WIN_SO_WEIGHT = 0.10
    LOSE_SO_WEIGHT = 0.05


class match_indecies(Enum):
    AWAY_TEAM = 0
    AWAY_SCORE = 1
    HOME_TEAM = 2
    HOME_SCORE = 3
    EXTRA_TIME = 4


def strength_of_schedule_get_dict() -> dict:
    return strength_of_schedule


def strength_of_schedule_get_games_played_dict() -> dict:
    return strength_of_schedule_games_played


def strength_of_schedule_get_trend_dict() -> dict:
    return strength_of_schedule_trends


def strength_of_schedule_get_data_set(match_data : dict={}) -> dict:
    game_value = {}
    home_team = match_data['linescore']["teams"]["home"]["team"]["name"]
    home_score_final = match_data['linescore']["teams"]["home"]["score"]
    away_team = match_data['linescore']["teams"]["away"]["team"]["name"]
    away_score_final = match_data['linescore']["teams"]["away"]["score"]
    final_game_state = match_data['linescore']["linescore"][
        "currentPeriodOrdinal"]

    # determine who won and lost the game
    if home_score_final > away_score_final:
        winner = home_team
        loser = away_team
    else:
        winner = away_team
        loser = home_team

    # now give points between 0 and 1 to each team depending on the game result
    if final_game_state == "3rd":
        game_value[winner] = \
            strength_of_schedule_weights.WIN_REGULATION_WEIGHT.value
        game_value[loser] = \
            strength_of_schedule_weights.LOSE_REGULATION_WEIGHT.value
    elif final_game_state == "OT":
        game_value[winner] = strength_of_schedule_weights.WIN_OT_WEIGHT.value
        game_value[loser] = strength_of_schedule_weights.LOSE_OT_WEIGHT.value
    else:
        game_value[winner] = strength_of_schedule_weights.WIN_SO_WEIGHT.value
        game_value[loser] = strength_of_schedule_weights.LOSE_OT_WEIGHT.value
    return game_value


def strength_of_schedule_add_match_data(sos_data : dict={}) -> None:
    for team in sos_data.keys():
        
        # first just increment the games played for each team which will be used
        # to scale the score later
        strength_of_schedule_games_played[team] += 1

        # then add the game value for this specific game to the unscaled result
        strength_of_schedule[team] += sos_data[team]


def strength_of_schedule_scale_by_game() -> None:

    # place the requried data into a dictionary for later use
    for team in strength_of_schedule.keys():
        strength_of_schedule[team] /= \
            strength_of_schedule_games_played[team]
