from enum import Enum

shots_for = {}

shots_for_unscaled = {}

goals_for = {}

goals_for_unscaled = {}

pp_goals = {}

pp_oppertunities = {}

pp_rating = {}

games_played = {}

offensive_rating = {}

offensive_rating_trends = {}

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
    return pp_rating


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

    for team in list(offensive_data[0].keys()):
        if team in shots_for.keys():

            # shots against
            shots_for_unscaled[team] += offensive_data[0][team]
            
            # goals against
            goals_for_unscaled[team] += offensive_data[1][team]
            
            # penalty kill
            pp_goals[team][0] += offensive_data[2][team]
            pp_oppertunities[team][1] += offensive_data[2][team]
            
            # games played
            games_played[team] += 1
        else:

            # shots against
            shots_for_unscaled[team] = offensive_data[0][team]
            
            # goals against
            goals_for_unscaled[team] = offensive_data[1][team]
            
            # penalty kill
            pp_goals[team][0] = offensive_data[2][team]
            pp_oppertunities[team][1] = offensive_data[2][team]

            # games played
            games_played[team] = 1


def offensive_rating_calculate_power_play() -> None:
    for team in shots_for_unscaled.keys():

        # shots for divided by game
        shots_for[team] = shots_for_unscaled[team] / games_played[team]

        # goals for divided by game
        goals_for[team] = goals_for_unscaled[team] / games_played[team]

        # pp converted to percentage
        if pp_oppertunities[team] > 0:
            pp_rating[team] = (pp_goals[team] / pp_oppertunities[team])
        else:
            pp_rating[team] = 0.0


def offensive_rating_combine_metrics() -> None:
    for team in shots_for.keys():
        offensive_rating[team] = (
            (shots_for[team] *
                offensive_rating_weights.SHOTS_PER_GAME.value) +
            (goals_for[team] *
                offensive_rating_weights.GOALS_PER_GAME.value) +
            (pp_rating[team] *
                offensive_rating_weights.POWER_PLAY_STRENGTH.value)
        )


def offensive_rating_update_trends() -> None:
    for team in offensive_rating.keys():
        if team in offensive_rating_trends.keys():
            offensive_rating_trends[team].append(offensive_rating[team])
        else:
            offensive_rating_trends[team] = list(offensive_rating[team])
