from enum import Enum

shots_against = {}

shots_against_unscaled = {}

goals_against = {}

goals_against_unscaled = {}

pk_goals_against = {}

pk_oppertunities = {}

pk_rating = {}

games_played = {}

defensive_rating = {}

defensive_rating_trends = {}

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
    return pk_rating


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


def defensive_rating_add_match_data(defensive_data : list=[]) -> None:
    for team in list(defensive_data[0].keys()):
        if team in shots_against_unscaled.keys():

            # shots against
            shots_against_unscaled[team] += defensive_data[0][team]
            
            # goals against
            goals_against_unscaled[team] += defensive_data[1][team]
            
            # penalty kill
            pk_goals_against[team] += defensive_data[2][team][0]
            pk_oppertunities[team] += defensive_data[2][team][1]
            
            # games played
            games_played[team] += 1
        else:

            # shots against
            shots_against_unscaled[team] = defensive_data[0][team]
            
            # goals against
            goals_against_unscaled[team] = defensive_data[1][team]
            
            # penalty kill
            pk_goals_against[team] = defensive_data[2][team][0]
            pk_oppertunities[team] = defensive_data[2][team][1]
            
            # games played
            games_played[team] = 1


def defensive_rating_calculate_all() -> None:
    for team in shots_against_unscaled.keys():

        # shots against divided by game
        shots_against[team] = shots_against_unscaled[team] / games_played[team]

        # goals against divided by game
        goals_against[team] = goals_against_unscaled[team] / games_played[team]

        # pk converted to percentage
        if pk_oppertunities[team] > 0:
            pk_rating[team] = (
                1.0 - (pk_goals_against[team] / pk_oppertunities[team])
            )
        else:
            pk_rating[team] = 0.0


def defensive_rating_combine_metrics() -> None:
    for team in shots_against.keys():
        defensive_rating[team] = (
            (shots_against[team] *
                defensive_rating_weights.SHOTS_AGAINST_PER_GAME.value) +
            (goals_against[team] *
                defensive_rating_weights.GOALS_AGAINST_PER_GAME.value) +
            (pk_rating[team] *
                defensive_rating_weights.PENALTY_KILL_STRENGTH.value)
        )


def defensive_rating_update_trends() -> None:
    for team in defensive_rating.keys():
        if team in defensive_rating_trends.keys():
            defensive_rating_trends[team].append(defensive_rating[team])
        else:
            defensive_rating_trends[team] = list(defensive_rating[team])