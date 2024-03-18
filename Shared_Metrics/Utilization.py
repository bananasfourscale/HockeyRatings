utilization_base_goalie = {}

utilization_base_defense = {}

utilization_base_forward = {}

utilization_rating_goalie = {}

utilization_rating_defense = {}

utilization_rating_forward = {}


def utilization_base_get_dict(position : str="") -> dict:
    if position == "G":
        return utilization_base_goalie
    if position == "D":
        return utilization_base_defense
    if position in ["C", "L", "R"]:
        return utilization_base_forward
    return {}
    

def utilization_rating_get_dict(position : str="") -> dict:
    if position == "G":
        return utilization_rating_goalie
    if position == "D":
        return utilization_rating_defense
    if position in ["C", "L", "R"]:
        return utilization_rating_forward
    return {}


def utilization_reset() -> None:
    utilization_base_goalie.clear()
    utilization_base_forward.clear()
    utilization_base_defense.clear()
    utilization_rating_goalie.clear()
    utilization_rating_forward.clear()
    utilization_rating_defense.clear()


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
    for player in utilization_data.keys():
        if position == "G":
            if player in utilization_base_goalie.keys():
                utilization_base_goalie[player] += \
                    utilization_data[player]["time_on_ice"]
            else:
                utilization_base_goalie[player] = \
                    utilization_data[player]["time_on_ice"]
        if position == "D":
            if player in utilization_base_defense.keys():
                utilization_base_defense[player] += \
                    utilization_data[player]["time_on_ice"]
            else:
                utilization_base_defense[player] = \
                    utilization_data[player]["time_on_ice"]
        if position in ["C", "L", "R"]:
            if player in utilization_base_forward.keys():
                utilization_base_forward[player] += \
                    utilization_data[player]["time_on_ice"]
            else:
                utilization_base_forward[player] = \
                    utilization_data[player]["time_on_ice"]


def utilization_scale_by_game(games_played : dict={}, teams_dict : dict={},
    position : str="") -> None:
    if position == "G":
        for player in utilization_base_goalie.keys():
            utilization_rating_goalie[player] = (
                utilization_base_goalie[player] /
                games_played[teams_dict[player]]
            )
    if position == "D":
        for player in utilization_base_defense.keys():
            utilization_rating_defense[player] = (
                utilization_base_defense[player] /
                games_played[teams_dict[player]]
            )
    if position in ["C", "L", "R"]:
        for player in utilization_base_forward.keys():
            utilization_rating_forward[player] = (
                utilization_base_forward[player] /
                games_played[teams_dict[player]]
            )
