from enum import Enum

shots_for = {}

goals_for = {}

power_play = {}

pp_oppertunities = {}

games_played = {}

offensive_rating = {}

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
    try:
        power_play_data[home_team] = [
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayOpportunities"]]
    except KeyError:
        power_play_data[home_team] = [
            match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            (match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["pim"] / 2)]
    
    # away data
    shots_for_data[away_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["shots"]
    goals_for_data[away_team] = match_data['boxscore']["teams"]["away"][
        "teamStats"]["teamSkaterStats"]["goals"]
    try:
        power_play_data[away_team] = [
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayOpportunities"]]
    except KeyError:
        power_play_data[away_team] = [
            match_data['boxscore']["teams"]["away"]["teamStats"][
                "teamSkaterStats"]["powerPlayGoals"],
            (match_data['boxscore']["teams"]["home"]["teamStats"][
                "teamSkaterStats"]["pim"] / 2)]
    return [shots_for_data, goals_for_data, power_play_data]


def offensive_rating_add_match_data(offensive_data : dict={}) -> None:

    home_team = list(offensive_data[0].keys())[0] 
    away_team = list(offensive_data[0].keys())[1]
    if home_team in shots_for.keys():

        # shots against
        shots_for[home_team] += \
            list(offensive_data[0].values())[0]
        
        # goals against
        goals_for[home_team] += \
            list(offensive_data[1].values())[0]
        
        # penalty kill
        power_play[home_team][0] += \
            list(offensive_data[2].values())[0][0]
        power_play[home_team][1] += \
            list(offensive_data[2].values())[0][1]
        
        # games played
        games_played[home_team] += 1
    else:

        # shots against
        shots_for[home_team] = \
            list(offensive_data[0].values())[0]

        # goals against
        goals_for[home_team] = \
            list(offensive_data[1].values())[0]
        
        # penalty kill
        power_play[home_team] = [list(offensive_data[2].values())[0][0],
            list(offensive_data[2].values())[0][1]]
        
        # add to games played
        games_played[home_team] = 1
        
    # away team
    if away_team in shots_for.keys():
        shots_for[away_team] += \
            list(offensive_data[0].values())[1]

        # goals against    
        goals_for[away_team] += \
            list(offensive_data[1].values())[1]

        # penalty kill stats (needs to be converted after collection)
        power_play[away_team][0] += \
            list(offensive_data[2].values())[1][0]
        power_play[away_team][1] += \
            list(offensive_data[2].values())[1][1]
        
        # add to games played
        games_played[away_team] += 1
    else:
        shots_for[away_team] = \
            list(offensive_data[0].values())[1]

        # goals against    
        goals_for[away_team] = \
            list(offensive_data[1].values())[1]

        # penalty kill stats (needs to be converted after collection)
        power_play[away_team] = [list(offensive_data[2].values())[1][0],
            list(offensive_data[2].values())[1][1]]
        
        # add to games played
        games_played[away_team] = 1


def offensive_rating_calculate_power_play() -> None:
    for team in power_play.keys():

        # shots for divided by game
        shots_for[team] /= games_played[team]

        # goals for divided by game
        goals_for[team] /= games_played[team]

        # pp converted to percentage
        pp_goals_for = power_play[team][0]
        pp_oppertunities[team] = power_play[team][1]
        if (pp_oppertunities[team] > 0):
            power_play[team] = (pp_goals_for / pp_oppertunities[team])
        else:
            power_play[team] = 0.0


def offensive_rating_combine_metrics(metric_list : list=[]) -> None:
    for team in metric_list[0].keys():
        offensive_rating[team] = \
            (metric_list[0][team] * \
                offensive_rating_weights.SHOTS_PER_GAME.value) + \
            (metric_list[1][team] * \
                offensive_rating_weights.GOALS_PER_GAME.value) + \
            (metric_list[2][team] * \
                offensive_rating_weights.POWER_PLAY_STRENGTH.value)
