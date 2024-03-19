multipoint_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

multipoint_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def multipoint_base_get_dict(position : str="") -> dict:
    if position in multipoint_base.keys():
        return multipoint_base[position]
    return {}


def multipoint_rating_get_dict(position : str="") -> dict:
    if position in multipoint_rating.keys():
        return multipoint_rating[position]
    return {}


def multipoint_reset() -> None:
    for key in multipoint_base.keys():
        multipoint_base[key].clear()
    for key in multipoint_rating.keys():
        multipoint_rating[key].clear()


def multipoint_get_data_set(match_data : dict={}) -> dict:
    multipoint = {}
    for player in match_data.keys():
        total_points = (
            match_data[player]['stats']['goals'] +
            match_data[player]['stats']['assists']
        )
        if total_points > 1:
            multipoint[player] = {'multipoint_games' : 1}
        else:
            multipoint[player] = {'multipoint_games' : 0}
    return multipoint


def multipoint_add_match_data(multipoint_data : dict={}, position : str="") \
                                                                        -> None:
    if position not in multipoint_base.keys():
        return {}
    for player in multipoint_data.keys():
        if player in multipoint_base[position].keys():
            multipoint_base[position][player] += \
                multipoint_data[player]["multipoint_games"]
        else:
            multipoint_base[position][player] = \
                multipoint_data[player]["multipoint_games"]
            

def multipoint_scale_by_game(team_games_played : dict={}, teams_dict : dict={},
    position : str="") -> None:
    if position not in multipoint_base.keys():
        return
    for player in multipoint_base[position].keys():
        multipoint_rating[position][player] = (
            multipoint_base[position][player] /
            team_games_played[teams_dict[player]]
        )
