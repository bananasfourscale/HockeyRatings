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


def offensive_rating_reset() -> None:
    shots_for.clear()
    shots_for_unscaled.clear()
    goals_for.clear()
    goals_for_unscaled.clear()
    pp_goals.clear()
    pp_oppertunities.clear()
    pp_rating.clear()
    games_played.clear()
    offensive_rating.clear()
    offensive_rating_trends.clear()


def offensive_rating_get_data_set(match_data : dict={}) -> list:

    # place the requried data into a dictionary for later use
    shots_for_data = {}
    goals_for_data = {}
    power_play_data = {}

    # get home and away team
    home_team = match_data['game_stats']['home_team']
    home_team_stats = match_data['game_stats'][home_team]["team_stats"]
    away_team = match_data['game_stats']['away_team']
    away_team_stats = match_data['game_stats'][away_team]["team_stats"]

    # home data
    shots_for_data[home_team] = home_team_stats["shots"]
    goals_for_data[home_team] = (
        home_team_stats["goals"] - (home_team_stats["empty_net_goals"] * 0.3)
    )
    power_play_data[home_team] = {
        'pp_goals_for' : (
            home_team_stats["power_play_goals"] -
            away_team_stats["short_handed_goals"]
        ),
        'pp_chances_for' : home_team_stats["power_play_chances"]
    }
    
    # away data
    shots_for_data[away_team] = away_team_stats["shots"]
    goals_for_data[away_team] = (
        away_team_stats["goals"] - (away_team_stats["empty_net_goals"] * 0.3)
    )
    power_play_data[away_team] = {
        'pp_goals_for' : (
            away_team_stats["power_play_goals"] -
            home_team_stats["short_handed_goals"]
        ),
        'pp_chances_for' : away_team_stats["power_play_chances"]
    }
    return {
        'shots_for' : shots_for_data,
        'goals_for' : goals_for_data,
        'power_play_data' : power_play_data
    }


def offensive_rating_add_match_data(offensive_data : dict={}) -> None:

    for team in list(offensive_data['shots_for'].keys()):
        if team in shots_for.keys():

            # shots for
            shots_for_unscaled[team] += offensive_data['shots_for'][team]
            
            # goals for
            goals_for_unscaled[team] += offensive_data['goals_for'][team]
            
            # power play
            pp_goals[team] += (
                offensive_data['power_play_data'][team]['pp_goals_for']
            )
            pp_oppertunities[team] += (
                offensive_data['power_play_data'][team]['pp_chances_for']
            )
            
            # games played
            games_played[team] += 1
        else:

            # shots for
            shots_for_unscaled[team] = offensive_data['shots_for'][team]
            
            # goals for
            goals_for_unscaled[team] = offensive_data['goals_for'][team]
            
            # power play
            pp_goals[team] = (
                offensive_data['power_play_data'][team]['pp_goals_for']
            )
            pp_oppertunities[team] = (
                offensive_data['power_play_data'][team]['pp_chances_for']
            )

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


def offensive_rating_update_trends(date : str="") -> None:
    offensive_rating_trends[date] = {}
    for team in offensive_rating.keys():
        offensive_rating_trends[date][team] = offensive_rating[team]
