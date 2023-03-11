from enum import Enum

shots_for = {
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

goals_for = {
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

power_play = {
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

offensive_rating_trends = {
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


pp_oppertunities = {}


class offensive_rating_weights(Enum):
    POWER_PLAY_STRENGTH = 0.20
    GOALS_PER_GAME = 0.50
    SHOTS_PER_GAME = 0.30


def offensive_rating_get_dict() -> dict:
    return offensive_rating


def offensive_rating_get_shots_for_dict() -> dict:
    return shots_for


def offensive_rating_get_goals_for_dict() -> dict:
    return goals_for


def offensive_rating_get_pp_dict() -> dict:
    return power_play


def offensive_rating_get_trend_dict() -> dict:
    return offensive_rating_trends


def offensive_rating_get_pp_oppertunities_dict() -> dict:
    return pp_oppertunities


def offensive_rating_get_data_set(match_data : dict={}) -> list:

    # place the requried data into a dictionary for later use
    shots_for_data = {}
    goals_for_data = {}
    power_play_data = {}

    # get home and away team
    home_team = match_data["linescore"]["teams"]["home"]["team"]["name"]
    away_team = match_data["linescore"]["teams"]["away"]["team"]["name"]

    # home data
    shots_for_data[home_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_for_data[home_team] = match_data['boxscore']["teams"]["home"][
        "teamStats"]["teamSkaterStats"]["goals"]
    power_play_data[home_team] = [
        match_data['boxscore']["teams"]["home"]["teamStats"][
            "teamSkaterStats"]["powerPlayGoals"],
        match_data['boxscore']["teams"]["home"]["teamStats"][
            "teamSkaterStats"]["powerPlayOpportunities"]]
    
    # away data
    shots_for_data[away_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_for_data[away_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["goals"]
    power_play_data[away_team] = [
        match_data['boxscore']["teams"]["away"]["teamStats"][
            "teamSkaterStats"]["powerPlayGoals"],
        match_data['boxscore']["teams"]["away"]["teamStats"][
            "teamSkaterStats"]["powerPlayOpportunities"]]
    return [shots_for_data, goals_for_data, power_play_data]


def offensive_rating_add_match_data(offensive_data : dict={}) -> None:
    # shots for
    shots_for[list(offensive_data[0].keys())[0]] += \
        list(offensive_data[0].values())[0]
    shots_for[list(offensive_data[0].keys())[1]] += \
        list(offensive_data[0].values())[1]

    # goals for
    goals_for[list(offensive_data[1].keys())[0]] += \
        list(offensive_data[1].values())[0]
    goals_for[list(offensive_data[1].keys())[1]] += \
        list(offensive_data[1].values())[1]

    # power play stats (needs to be converted after collection)
    power_play[list(offensive_data[2].keys())[0]][0] += \
        list(offensive_data[2].values())[0][0]
    power_play[list(offensive_data[2].keys())[0]][1] += \
        list(offensive_data[2].values())[0][1]
    power_play[list(offensive_data[2].keys())[1]][0] += \
        list(offensive_data[2].values())[1][0]
    power_play[list(offensive_data[2].keys())[1]][1] += \
        list(offensive_data[2].values())[1][1]


def offensive_rating_calculate_power_play() -> None:
    for team in power_play.keys():
        pp_goals_for = power_play[team][0]
        pp_oppertunities[team] = power_play[team][1]
        if (pp_oppertunities[team] > 0):
            power_play[team] = (pp_goals_for / pp_oppertunities[team])
        else:
            power_play[team] = 0.0


def offensive_rating_combine_metrics(metric_list : list=[]) -> None:
    for team in offensive_rating.keys():
        offensive_rating[team] = \
            (metric_list[0][team] * \
                offensive_rating_weights.SHOTS_PER_GAME.value) + \
            (metric_list[1][team] * \
                offensive_rating_weights.GOALS_PER_GAME.value) + \
            (metric_list[2][team] * \
                offensive_rating_weights.POWER_PLAY_STRENGTH.value)
