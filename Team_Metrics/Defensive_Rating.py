from enum import Enum

shots_against = {
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

shots_against_unscaled = {
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

goals_against = {
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

penalty_kill = {
    'Anaheim Ducks' : [0,0],
    'Arizona Coyotes' : [0,0],
    'Boston Bruins' : [0,0],
    'Buffalo Sabres' : [0,0],
    'Calgary Flames' : [0,0],
    'Carolina Hurricanes' : [0,0],
    'Chicago Blackhawks' : [0,0],
    'Colorado Avalanche' : [0,0],
    'Columbus Blue Jackets' : [0,0],
    'Dallas Stars' : [0,0],
    'Detroit Red Wings' : [0,0],
    'Edmonton Oilers' : [0,0],
    'Florida Panthers' : [0,0],
    'Los Angeles Kings' : [0,0],
    'Minnesota Wild' : [0,0],
    'Montréal Canadiens' : [0,0],
    'Nashville Predators' : [0,0],
    'New Jersey Devils' : [0,0],
    'New York Islanders' : [0,0],
    'New York Rangers' : [0,0],
    'Ottawa Senators' : [0,0],
    'Philadelphia Flyers' : [0,0],
    'Pittsburgh Penguins' : [0,0],
    'San Jose Sharks' : [0,0],
    'Seattle Kraken' : [0,0],
    'St. Louis Blues' : [0,0],
    'Tampa Bay Lightning' : [0,0],
    'Toronto Maple Leafs' : [0,0],
    'Vancouver Canucks' : [0,0],
    'Vegas Golden Knights' : [0,0],
    'Washington Capitals' : [0,0],
    'Winnipeg Jets' : [0,0],
}

games_played = {
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

defensive_rating_trends = {
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

pk_oppertunities = {}

class defensive_rating_weights(Enum):
    PENALTY_KILL_STRENGTH = 0.20
    GOALS_AGAINST_PER_GAME = 0.50
    SHOTS_AGAINST_PER_GAME = 0.30


def defensive_rating_get_dict() -> dict:
    return defensive_rating


def defensive_rating_get_shots_against_dict() -> dict:
    return shots_against


def defensive_rating_get_unscaled_shots_against_dict() -> dict:
    return shots_against_unscaled


def defensive_rating_get_goals_against_dict() -> dict:
    return goals_against


def defensive_rating_get_pk_dict() -> dict:
    return penalty_kill


def defensive_rating_get_trend_dict() -> dict:
    return defensive_rating_trends


def defensive_rating_get_pk_oppertunities_dict() -> dict:
    return pk_oppertunities


def defensive_rating_get_data_set(match_data : dict={}) -> list:

    # place the requried data into a dictionary for later use
    shots_against_data = {}
    goals_against_data = {}
    penalty_kill_data = {}

    # get home and away team
    home_team = match_data["linescore"]["teams"]["home"]["team"]["name"]
    away_team = match_data["linescore"]["teams"]["away"]["team"]["name"]

    # home data
    shots_against_data[home_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_against_data[home_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["goals"]
    penalty_kill_data[home_team] = [
        match_data['boxscore']["teams"]["away"]["teamStats"][
            "teamSkaterStats"]["powerPlayGoals"],
        match_data['boxscore']["teams"]["away"]["teamStats"][
            "teamSkaterStats"]["powerPlayOpportunities"]]

    # away data
    shots_against_data[away_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_against_data[away_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["goals"]
    penalty_kill_data[away_team] = [
        match_data['boxscore']["teams"]["home"]["teamStats"][
            "teamSkaterStats"]["powerPlayGoals"],
        match_data['boxscore']["teams"]["home"]["teamStats"][
            "teamSkaterStats"]["powerPlayOpportunities"]]
    return [shots_against_data, goals_against_data, penalty_kill_data]


def defensive_rating_add_match_data(defensive_data : dict={}) -> None:

    # shots against
    shots_against[list(defensive_data[0].keys())[0]] += \
        list(defensive_data[0].values())[0]
    shots_against[list(defensive_data[0].keys())[1]] += \
        list(defensive_data[0].values())[1]
    shots_against_unscaled[list(defensive_data[0].keys())[0]] += \
        list(defensive_data[0].values())[0]
    shots_against_unscaled[list(defensive_data[0].keys())[1]] += \
        list(defensive_data[0].values())[1]

    # goals against
    goals_against[list(defensive_data[1].keys())[0]] += \
        list(defensive_data[1].values())[0]
    goals_against[list(defensive_data[1].keys())[1]] += \
        list(defensive_data[1].values())[1]

    # penalty kill stats (needs to be converted after collection)
    penalty_kill[list(defensive_data[2].keys())[0]][0] += \
        list(defensive_data[2].values())[0][0]
    penalty_kill[list(defensive_data[2].keys())[0]][1] += \
        list(defensive_data[2].values())[0][1]
    penalty_kill[list(defensive_data[2].keys())[1]][0] += \
        list(defensive_data[2].values())[1][0]
    penalty_kill[list(defensive_data[2].keys())[1]][1] += \
        list(defensive_data[2].values())[1][1]
    
    # add to games played
    games_played[list(defensive_data[0].keys())[0]] += 1
    games_played[list(defensive_data[0].keys())[1]] += 1


def defensive_rating_calculate_all() -> None:
    for team in penalty_kill.keys():

        # shots against divided by game
        shots_against[team] /= games_played[team]

        # goals against divided by game
        goals_against[team] /= games_played[team]

        # pk converted to percentage
        pk_goals_against = penalty_kill[team][0]
        pk_oppertunities[team] = penalty_kill[team][1]
        if (pk_oppertunities[team] > 0):
            penalty_kill[team] = \
                1.0 - (pk_goals_against / pk_oppertunities[team])
        else:
            penalty_kill[team] = 0.0


def defensive_rating_combine_metrics(metric_list : list=[]) -> None:
    for team in defensive_rating.keys():
        defensive_rating[team] = \
            (metric_list[0][team] * \
                defensive_rating_weights.SHOTS_AGAINST_PER_GAME.value) + \
            (metric_list[1][team] * \
                defensive_rating_weights.GOALS_AGAINST_PER_GAME.value) + \
            (metric_list[2][team] * \
                defensive_rating_weights.PENALTY_KILL_STRENGTH.value)
