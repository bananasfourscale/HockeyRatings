from enum import Enum

shots_against = {}

shots_against_unscaled = {}

goals_against = {}

penalty_kill = {}

pk_oppertunities = {}

games_played = {}

defensive_rating = {}

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
    try:
        penalty_kill_data[home_team] = [
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayOpportunities"]]
    except KeyError:
        penalty_kill_data[home_team] = [
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            (match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["pim"] / 2)]

    # away data
    shots_against_data[away_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_against_data[away_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["goals"]
    try:
        penalty_kill_data[away_team] = [
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayOpportunities"]]
    except KeyError:
        penalty_kill_data[away_team] = [
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            (match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["pim"] / 2)]
    return [shots_against_data, goals_against_data, penalty_kill_data]


def defensive_rating_add_match_data(defensive_data : dict={}) -> None:

    # home team
    home_team = list(defensive_data[0].keys())[0] 
    away_team = list(defensive_data[0].keys())[1] 
    if home_team in shots_against.keys():

        # shots against
        shots_against[home_team] += \
            list(defensive_data[0].values())[0]
        shots_against_unscaled[home_team] += \
            list(defensive_data[0].values())[0]
        
        # goals against
        goals_against[home_team] += \
            list(defensive_data[1].values())[0]
        
        # penalty kill
        penalty_kill[home_team][0] += \
            list(defensive_data[2].values())[0][0]
        penalty_kill[home_team][1] += \
            list(defensive_data[2].values())[0][1]
        
        # games played
        games_played[home_team] += 1
    else:

        # shots against
        shots_against[home_team] = \
            list(defensive_data[0].values())[0]
        shots_against_unscaled[home_team] = \
            list(defensive_data[0].values())[0]
        
        # goals against
        goals_against[home_team] = \
            list(defensive_data[1].values())[0]
        
        # penalty kill
        penalty_kill[home_team] = [list(defensive_data[2].values())[0][0],
            list(defensive_data[2].values())[0][1]]
        
        # games played
        games_played[home_team] = 1
        
    # away team
    if away_team in shots_against.keys():

        shots_against[away_team] += \
            list(defensive_data[0].values())[1]
        shots_against_unscaled[away_team] += \
            list(defensive_data[0].values())[1]

        # goals against    
        goals_against[away_team] += \
            list(defensive_data[1].values())[1]

        # penalty kill stats (needs to be converted after collection)
        penalty_kill[away_team][0] += \
            list(defensive_data[2].values())[1][0]
        penalty_kill[away_team][1] += \
            list(defensive_data[2].values())[1][1]
    
        # add to games played
        games_played[away_team] += 1
    else:

        shots_against[away_team] = \
            list(defensive_data[0].values())[1]
        shots_against_unscaled[away_team] = \
            list(defensive_data[0].values())[1]

        # goals against    
        goals_against[away_team] = \
            list(defensive_data[1].values())[1]

        # penalty kill stats (needs to be converted after collection)
        penalty_kill[away_team] = [list(defensive_data[2].values())[1][0],
            list(defensive_data[2].values())[1][1]]
    
        # add to games played
        games_played[away_team] = 1


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
    for team in metric_list[0].keys():
        defensive_rating[team] = \
            (metric_list[0][team] * \
                defensive_rating_weights.SHOTS_AGAINST_PER_GAME.value) + \
            (metric_list[1][team] * \
                defensive_rating_weights.GOALS_AGAINST_PER_GAME.value) + \
            (metric_list[2][team] * \
                defensive_rating_weights.PENALTY_KILL_STRENGTH.value)
