forward_contribution_base = {}

forward_contributing_games_rating = {}


def forward_contributing_games_get_dict() -> dict:
    return forward_contributing_games_rating


def forward_contributing_games_get_data_set(match_data : dict={}) -> list:
    contributing_game = {}

    for forward in match_data.keys():
        total_points = \
            match_data[forward][1]["goals"] + match_data[forward][1]["assists"]

        # if they score this game then 1 otherwise 0
        if total_points >= 1:
            contributing_game[forward] = [match_data[forward][0], 1]
        else:
            contributing_game[forward] = [match_data[forward][0], 0]
    return contributing_game


def forward_contributing_games_add_match_data(
    forward_contribution_data : dict={}) -> None:
    for forward in forward_contribution_data.keys():
        if forward in forward_contribution_base.keys():
            forward_contribution_base[forward] += \
                forward_contribution_data[forward][1]
        else:
            forward_contribution_base[forward] = \
                forward_contribution_data[forward][1]
            

def forward_contributing_games_scale_by_games(
    teams_games_played : dict={}, forward_teams_dict : dict={}) -> None:
    for forward in forward_contribution_base.keys():
        forward_contributing_games_rating[forward] = (
            forward_contribution_base[forward] /
                teams_games_played[forward_teams_dict[forward]]
        )
