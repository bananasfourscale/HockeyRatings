goalie_save_consistency_base = {}

goalie_save_consistency_rating = {}


def goalie_save_consistency_get_dict() -> dict:
    return goalie_save_consistency_rating


def goalie_save_consistency_reset() -> None:
    goalie_save_consistency_base.clear()
    goalie_save_consistency_rating.clear()


def goalie_save_consistency_get_data_set(match_data : dict={}) -> dict:
    save_consistency = {}
    for goalie in match_data.keys():
        shot_total = (
            match_data[goalie]['stats']["even_shots"] + 
            match_data[goalie]['stats']["power_play_shots"] + 
            match_data[goalie]['stats']["short_handed_shots"]
        )
        save_total = (
            match_data[goalie]['stats']["even_saves"] + 
            match_data[goalie]['stats']["power_play_saves"] + 
            match_data[goalie]['stats']["short_handed_saves"]
        )
        if shot_total > 0:
            save_consistency_game = save_total / shot_total
        else:
            save_consistency_game = 0

        # a game with 90%+ save per is considered standard.
        if save_consistency_game > 0.9:
            save_consistency[goalie] = 1
        else:
            save_consistency[goalie] = 0
    return save_consistency


def goalie_save_consistency_add_match_data(
    goalie_save_consistency_data : dict={}) -> None:
    for goalie in goalie_save_consistency_data.keys():
        if goalie in goalie_save_consistency_base.keys():
            goalie_save_consistency_base[goalie] += \
                goalie_save_consistency_data[goalie]
        else:
            goalie_save_consistency_base[goalie] = \
                goalie_save_consistency_data[goalie]
            

def goalie_save_consistency_scale_by_games(teams_games_played : dict={},
    goalie_teams_dict : dict={}) -> None:
    for goalie in goalie_save_consistency_base.keys():
        goalie_save_consistency_rating[goalie] = (
            goalie_save_consistency_base[goalie] /
                teams_games_played[goalie_teams_dict[goalie]]
        )
