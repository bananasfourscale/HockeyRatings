hitting_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

hitting_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def hitting_base_get_dict(position : str="") -> dict:
    if position in hitting_base.keys():
        return hitting_base[position]
    return {}


def hitting_rating_get_dict(position : str="") -> dict:
    if position in hitting_rating.keys():
        return hitting_rating[position]
    return {}


def hitting_reset() -> None:
    for key in hitting_base.keys():
        hitting_base[key].clear()
    for key in hitting_rating.keys():
        hitting_rating[key].clear()


def hitting_get_data_set(match_data : dict={}) -> dict:
    hitting = {}
    for player in match_data.keys():
        hitting[player] = {
            'hitting' : match_data[player]['stats']['hits'] -
                (match_data[player]['stats']['hits_taken'] * 0.25)
        }
    return hitting


def hitting_add_match_data(hitting_data : dict={}, position : str="") -> None:
    if position not in hitting_base.keys():
        return {}
    for player in hitting_data.keys():
        if player in hitting_base[position].keys():
            hitting_base[position][player] += \
                hitting_data[player]["hitting"]
        else:
            hitting_base[position][player] = \
                hitting_data[player]["hitting"]
                

def hitting_scale_by_game(team_games_played : dict={}, teams_dict : dict={},
    position : str="") -> None:
    if position not in hitting_base.keys():
        return
    for player in hitting_base[position].keys():
        hitting_rating[position][player] = (
            hitting_base[position][player] /
            team_games_played[teams_dict[player]]
        )
