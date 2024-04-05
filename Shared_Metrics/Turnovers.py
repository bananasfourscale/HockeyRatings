turnovers_base = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

turnovers_rating = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def turnovers_base_get_dict(position : str="") -> dict:
    if position in turnovers_base.keys():
        return turnovers_base[position]
    return {}


def turnovers_rating_get_dict(position : str="") -> dict:
    if position in turnovers_rating.keys():
        return turnovers_rating[position]
    return {}


def turnovers_reset() -> None:
    for key in turnovers_base.keys():
        turnovers_base[key].clear()
    for key in turnovers_rating.keys():
        turnovers_rating[key].clear()


def turnovers_get_data_set(players : dict={}) -> dict:
    turnovers = {}
    for player in players.keys():
        turnovers[player] = {
            'turnovers' : (
                players[player]['stats']['takeaways'] -
                players[player]['stats']['giveaways']
            )
        }
    return turnovers


def turnovers_add_match_data(turnovers_data : dict = {}, position : str="") \
                                                                        -> None:
    if position not in turnovers_base.keys():
        return {}
    for player in turnovers_data.keys():
        if player in turnovers_base[position].keys():
            turnovers_base[position][player] += \
                turnovers_data[player]["turnovers"]
        else:
            turnovers_base[position][player] = \
                turnovers_data[player]["turnovers"]
                

def turnovers_scale_by_utilization(utilization : dict={}, position : str="")\
                                                                        -> None:
    if position not in turnovers_base.keys():
        return
    for player in turnovers_base[position].keys():
        turnovers_rating[position][player] = (
            turnovers_base[position][player] * utilization[player]
        )
