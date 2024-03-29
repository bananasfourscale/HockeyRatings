from enum import Enum

strength_of_schedule = {}

strength_of_schedule_games_played = {}

sos_rating = {}

strength_of_schedule_trends = {}

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
    return sos_rating


def strength_of_schedule_get_games_played_dict() -> dict:
    return strength_of_schedule_games_played


def strength_of_schedule_get_trend_dict() -> dict:
    return strength_of_schedule_trends


def strength_of_schedule_reset() -> None:
    strength_of_schedule.clear()
    strength_of_schedule_games_played.clear()
    sos_rating.clear()
    strength_of_schedule_trends.clear()


def strength_of_schedule_get_data_set(match_data : dict={}) -> dict:
    game_value = {}
    home_team = match_data['game_stats']['home_team']
    home_team_stats = match_data['game_stats'][home_team]["team_stats"]
    away_team = match_data['game_stats']['away_team']
    away_team_stats = match_data['game_stats'][away_team]["team_stats"]
    home_score_final = (
        home_team_stats["first_period_goals"] +
        home_team_stats["second_period_goals"] +
        home_team_stats["third_period_goals"] + home_team_stats["OT_goals"] +
        home_team_stats["SO_goals"]
    )
    away_score_final = (
        away_team_stats["first_period_goals"] +
        away_team_stats["second_period_goals"] +
        away_team_stats["third_period_goals"] + away_team_stats["OT_goals"] +
        away_team_stats["SO_goals"]
    )
    final_game_state = match_data['game_stats']['result']

    # determine who won and lost the game
    if home_score_final > away_score_final:
        winner = home_team
        loser = away_team
    else:
        winner = away_team
        loser = home_team

    # now give points between 0 and 1 to each team depending on the game result
    if final_game_state == "REG":
        game_value[winner] = \
            strength_of_schedule_weights.WIN_REGULATION_WEIGHT.value
        game_value[loser] = \
            strength_of_schedule_weights.LOSE_REGULATION_WEIGHT.value
    elif final_game_state == "OT":
        game_value[winner] = strength_of_schedule_weights.WIN_OT_WEIGHT.value
        game_value[loser] = strength_of_schedule_weights.LOSE_OT_WEIGHT.value
    else:
        game_value[winner] = strength_of_schedule_weights.WIN_SO_WEIGHT.value
        game_value[loser] = strength_of_schedule_weights.LOSE_SO_WEIGHT.value
    return game_value


def strength_of_schedule_add_match_data(sos_data : dict={}) -> None:
    for team in sos_data.keys():
        
        # add games played and sos data for each team to be scaled later
        if team in strength_of_schedule_games_played.keys():
            strength_of_schedule_games_played[team] += 1
            strength_of_schedule[team] += sos_data[team]
        else:
            strength_of_schedule_games_played[team] = 1
            strength_of_schedule[team] = sos_data[team]


def strength_of_schedule_scale_by_game() -> None:

    # place the requried data into a dictionary for later use
    for team in strength_of_schedule.keys():
        sos_rating[team] = (
            strength_of_schedule[team] / strength_of_schedule_games_played[team]
        )


def strength_of_schedule_update_trends(date : str="") -> None:
    strength_of_schedule_trends[date] = {}
    for team in sos_rating.keys():
        strength_of_schedule_trends[date][team] = sos_rating[team]
