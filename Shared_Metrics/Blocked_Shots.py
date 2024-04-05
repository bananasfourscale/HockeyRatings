blocks_base_forward = {}

blocks_rating_forward = {}

blocks_base_defense = {}

blocks_rating_defense = {}

blocks_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

blocks_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

def blocks_base_get_dict(position : str="") -> dict:
    if position in blocks_base.keys():
        return blocks_base[position]
    return {}


def blocks_rating_get_dict(position : str="") -> dict:
    if position in blocks_rating.keys():
        return blocks_rating[position]
    return {}


def blocks_reset() -> None:
    for key in blocks_base.keys():
        blocks_base[key].clear()
    for key in blocks_rating.keys():
        blocks_rating[key].clear()


def blocks_get_data_set(players : dict={}) -> dict:
    blocks = {}
    for player in players.keys():
        blocks[player] = {'blocks' : players[player]['stats']['blocks']}
    return blocks


def blocks_add_match_data(blocks_data : dict={}, position : str="") -> None:
    if position not in blocks_base.keys():
        return {}
    for player in blocks_data.keys():
        if player in blocks_base[position].keys():
            blocks_base[position][player] += blocks_data[player]['blocks']
        else:
            blocks_base[position][player] = blocks_data[player]['blocks']


def blocks_scale_by_shots_against(team_shots_against : dict={},
    teams_dict : dict={}, position : str="") -> None:
    if position not in blocks_base.keys():
        return
    for player in blocks_base[position].keys():
        blocks_rating[position][player] = (
            blocks_base[position][player] /
            team_shots_against[teams_dict[player]]
        )
