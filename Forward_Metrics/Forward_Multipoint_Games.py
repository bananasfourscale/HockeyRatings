forward_multipoint_base = {}

forward_multipoint_games_rating = {}


def forward_multipoint_games_get_dict() -> dict:
    return forward_multipoint_games_rating


def forward_multipoint_games_reset() -> None:
    forward_multipoint_base.clear()
    forward_multipoint_games_rating.clear()


def forward_multipoint_games_get_data_set(match_data : dict={}) -> list:
    multipoint_game = {}

    for forward in match_data.keys():
        total_points = \
            match_data[forward][1]["goals"] + match_data[forward][1]["assists"]

        # if they score this game then 1 otherwise 0
        if total_points > 1:
            multipoint_game[forward] = [match_data[forward][0], 1]
        else:
            multipoint_game[forward] = [match_data[forward][0], 0]
    return multipoint_game


def forward_multipoint_games_add_match_data(
    forward_contribution_data : dict={}) -> None:
    for forward in forward_contribution_data.keys():
        if forward in forward_multipoint_base.keys():
            forward_multipoint_base[forward] += \
                forward_contribution_data[forward][1]
        else:
            forward_multipoint_base[forward] = \
                forward_contribution_data[forward][1]
            

def forward_multipoint_games_scale_by_games(teams_games_played : dict={},
    forward_teams_dict : dict={}) -> None:
    for forward in forward_multipoint_base.keys():
        forward_multipoint_games_rating[forward] = (
            forward_multipoint_base[forward] /
                teams_games_played[forward_teams_dict[forward]]
        )
