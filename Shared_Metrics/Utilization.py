utilization_base = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

utilization_rating = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

def utilization_base_get_dict(position : str="") -> dict:
    if position in utilization_base.keys():
        return utilization_base[position]
    return {}
    

def utilization_rating_get_dict(position : str="") -> dict:
    if position in utilization_rating.keys():
        return utilization_rating[position]
    return {}


def utilization_reset() -> None:
    for key in utilization_base.keys():
        utilization_base[key].clear()
    for key in utilization_rating.keys():
        utilization_rating[key].clear()


def utilization_get_data_set(match_data : dict={}) -> dict:
    utilization = {}
    for player in match_data.keys():

        # convert time on ice to minutes
        time_on_ice = \
            float(match_data[player]['stats']['time_on_ice'].split(":")[0]) + \
            float(match_data[player]['stats']['time_on_ice'].split(":")[1]) / 60
        utilization[player] = {
            'team' : match_data[player]['team'],
            "time_on_ice" : time_on_ice
        }
    return utilization


def utilization_add_match_data(utilization_data : dict={}, position : str="") \
                                                                        -> None:
    if position not in utilization_base.keys():
        return {}
    for player in utilization_data.keys():
        if player in utilization_base[position].keys():
            utilization_base[position][player] += \
                utilization_data[player]["time_on_ice"]
        else:
            utilization_base[position][player] = \
                utilization_data[player]["time_on_ice"]


def utilization_scale_by_game(team_games_played : dict={}, teams_dict : dict={},
    position : str="") -> None:
    if position not in utilization_base.keys():
        return
    for player in utilization_base[position].keys():
        utilization_rating[position][player] = (
            utilization_base[position][player] /
            team_games_played[teams_dict[player]]
        )
