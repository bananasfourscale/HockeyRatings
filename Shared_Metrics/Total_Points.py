total_points_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

total_points_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def total_points_base_get_dict(position : str="") -> dict:
    if position in total_points_base.keys():
        return total_points_base[position]
    return {}


def total_points_rating_get_dict(position : str="") -> dict:
    if position in total_points_rating.keys():
        return total_points_rating[position]
    return {}


def total_points_reset() -> None:
    for key in total_points_base.keys():
        total_points_base[key].clear()
    for key in total_points_rating.keys():
        total_points_rating[key].clear()


def total_points_get_data_set(match_data : dict={}) -> dict:
    total_points = {}
    for player in match_data.keys():
        total_points[player] = {
            'total_points' : (
                match_data[player]['stats']['goals'] +
                (match_data[player]['stats']['assists'] * 0.90)
            )
        }
    return total_points


def total_points_add_match_data(total_points_data : dict={}, position : str="") \
                                                                        -> None:
    if position not in total_points_base.keys():
        return {}
    for player in total_points_data.keys():
        if player in total_points_base[position].keys():
            total_points_base[position][player] += \
                total_points_data[player]["total_points"]
        else:
            total_points_base[position][player] = \
                total_points_data[player]["total_points"]
                

def total_points_scale_by_game(team_games_played : dict={},
    teams_dict : dict={}, position : str="") -> None:
    if position not in total_points_base.keys():
        return
    for player in total_points_base[position].keys():
        total_points_rating[position][player] = (
            total_points_base[position][player] /
            team_games_played[teams_dict[player]]
        )
