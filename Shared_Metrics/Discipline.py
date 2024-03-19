discipline_base = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

discipline_rating = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def discipline_base_get_dict(position : str="") -> dict:
    if position in discipline_base.keys():
        return discipline_base[position]
    return {}


def discipline_rating_get_dict(position : str="") -> dict:
    if position in discipline_rating.keys():
        return discipline_rating[position]
    return {}


def discipline_reset() -> None:
    for key in discipline_base.keys():
        discipline_base[key].clear()
    for key in discipline_rating.keys():
        discipline_rating[key].clear()


def discipline_get_data_set(match_data : dict={}) -> dict:
    discipline = {}
    for player in match_data.keys():
        discipline[player] = {
            'penalty_net_minutes' : 
                match_data[player]['stats']['penalty_minutes'] -
                match_data[player]['stats']['penalty_minutes_drawn']
        }
    return discipline


def discipline_add_match_data(discipline_data : dict = {}, position : str="") \
                                                                        -> None:
    if position not in discipline_base.keys():
        return {}
    for player in discipline_data.keys():
        if player in discipline_base[position].keys():
            discipline_base[position][player] += \
                discipline_data[player]["penalty_net_minutes"]
        else:
            discipline_base[position][player] = \
                discipline_data[player]["penalty_net_minutes"]
                

def discipline_scale_by_utilization(utilization : dict={}, position : str="")\
                                                                        -> None:
    if position not in discipline_base.keys():
        return
    for player in discipline_base[position].keys():
        discipline_rating[position][player] = (
            discipline_base[position][player] * (1 - utilization[player])
        )
