plus_minus_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

plus_minus_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

def plus_minus_base_get_dict(position : str="") -> dict:
    if position in plus_minus_base.keys():
        return plus_minus_base[position]
    return {}
    

def plus_minus_rating_get_dict(position : str="") -> dict:
    if position in plus_minus_rating.keys():
        return plus_minus_rating[position]
    return {}


def plus_minus_reset() -> None:
    for key in plus_minus_base.keys():
        plus_minus_base[key].clear()
    for key in plus_minus_rating.keys():
        plus_minus_rating[key].clear()


def plus_minus_get_data_set(players : dict={}) -> dict:
    plus_minus = {}
    for player in players.keys():

        # convert time on ice to minutes
        plus_minus[player] = {
            "plus_minus" : players[player]['stats']['plus_minus']
        }
    return plus_minus


def plus_minus_add_match_data(plus_minus_data : dict={}, position : str="") \
                                                                        -> None:
    if position not in plus_minus_base.keys():
        return {}
    for player in plus_minus_data.keys():
        if player in plus_minus_base[position].keys():
            plus_minus_base[position][player] += \
                plus_minus_data[player]["plus_minus"]
        else:
            plus_minus_base[position][player] = \
                plus_minus_data[player]["plus_minus"]
            

def plus_minus_scale_by_utilization(utilization : dict={}, position : str="")\
                                                                        -> None:
    if position not in plus_minus_base.keys():
        return
    for player in plus_minus_base[position].keys():
        plus_minus_rating[position][player] = (
            plus_minus_base[position][player] * utilization[player]
        )
