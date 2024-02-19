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


def defensive_rating_reset() -> None:
    shots_against.clear()
    shots_against_unscaled.clear()
    goals_against.clear()
    goals_against_unscaled.clear()
    pk_goals_against.clear()
    pk_oppertunities.clear()
    pk_rating.clear()
    games_played.clear()
    defensive_rating.clear()
    defensive_rating_trends.clear()

def defensive_rating_get_data_set(match_data : dict={}) -> list:

    # place the requried data into a dictionary for later use
    shots_against_data = {}
    goals_against_data = {}
    penalty_kill_data = {}

    # get home and away team
    home_team = match_data['game_stats']['home_team']
    home_team_stats = match_data['game_stats'][home_team]["team_stats"]
    away_team = match_data['game_stats']['away_team']
    away_team_stats = match_data['game_stats'][away_team]["team_stats"]

    # home data
    shots_against_data[home_team] = away_team_stats["shots"]
    goals_against_data[home_team] = away_team_stats["first_period_goals"] + \
        away_team_stats["second_period_goals"] + \
        away_team_stats["third_period_goals"]
    try:
        penalty_kill_data[home_team] = [
            away_team_stats["power_play_goals"],
            away_team_stats["power_play_chances"]
        ]
    except KeyError:
        penalty_kill_data[home_team] = [
            away_team_stats["power_play_goals"],
            away_team_stats["penalty_minutes"] / 2
        ]

    # away data
    shots_against_data[away_team] = home_team_stats["shots"]
    goals_against_data[away_team] = home_team_stats["first_period_goals"] + \
        home_team_stats["second_period_goals"] + \
        home_team_stats["third_period_goals"]
    try:
        penalty_kill_data[away_team] = [
            home_team_stats["power_play_goals"],
            home_team_stats["power_play_chances"]
        ]
    except KeyError:
        penalty_kill_data[away_team] = [
            home_team_stats["power_play_goals"],
            home_team_stats["penalty_minutes"] / 2
        ]
    return {
        'shots_against' : shots_against_data,
        'goals_against' : goals_against_data,
        'penalty_kill_data' : penalty_kill_data
    }


def defensive_rating_add_match_data(defensive_data : list=[]) -> None:
    for team in list(defensive_data['shots_against'].keys()):
        if team in shots_against_unscaled.keys():

            # shots against
            shots_against_unscaled[team] += \
                defensive_data['shots_against'][team]
            
            # goals against
            goals_against_unscaled[team] += \
                defensive_data['goals_against'][team]
            
            # penalty kill
            pk_goals_against[team] += \
                defensive_data['penalty_kill_data'][team][0]
            pk_oppertunities[team] += \
                defensive_data['penalty_kill_data'][team][1]
            
            # games played
            games_played[team] += 1
        else:

            # shots against
            shots_against_unscaled[team] = \
                defensive_data['shots_against'][team]
            
            # goals against
            goals_against_unscaled[team] = \
                defensive_data['goals_against'][team]
            
            # penalty kill
            pk_goals_against[team] = \
                defensive_data['penalty_kill_data'][team][0]
            pk_oppertunities[team] = \
                defensive_data['penalty_kill_data'][team][1]
            
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


def defensive_rating_update_trends(date : str="") -> None:
    defensive_rating_trends[date] = {}
    for team in defensive_rating.keys():
        defensive_rating_trends[date][team] = defensive_rating[team]
