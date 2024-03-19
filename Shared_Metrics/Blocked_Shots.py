blocks_base_forward = {}

blocks_rating_forward = {}

blocks_base_defense = {}

blocks_rating_defense = {}

def blocks_base_get_dict(position : str="") -> dict:
    if position == "D":
        return blocks_base_defense
    if position in ["C", "L", "R"]:
        return blocks_base_forward
    return {}


def blocks_rating_get_dict(position : str="") -> dict:
    if position == "D":
        return blocks_rating_defense
    if position in ["C", "L", "R"]:
        return blocks_rating_forward
    return {}


def blocks_reset() -> None:
    blocks_base_forward.reset()
    blocks_rating_forward.reset()
    blocks_base_defense.reset()
    blocks_rating_defense.reset()


def blocks_get_data_set(match_data : dict={}) -> dict:
    blocks = {}
    for player in match_data.keys():
        blocks[player] = {'blocks' : match_data[player]['stats']['blocks']}


def blocks_add_match_data(blocks_data : dict={}, position : str="") -> None:
    for player in blocks_data.keys():
        if position == "D":
            if player in blocks_base_defense.keys():
                blocks_base_defense[player] += blocks_data[player]['blocks']
            else:
                blocks_base_defense[player] = blocks_data[player]['blocks']
        if position in ["C", "L", "R"]:
            if player in blocks_base_forward.keys():
                blocks_base_forward[player] += blocks_data[player]['blocks']
            else:
                blocks_base_forward[player] = blocks_data[player]['blocks']


def blocks_scale_by_shots_against(team_shots_against : dict={},
    teams_dict : dict={}, position : str="") -> None:
    if position == "D":
        for player in blocks_base_defense.keys():
            blocks_rating_defense[player] = (
                blocks_base_defense / team_shots_against[teams_dict[player]]
            )
    if position in ["C", "L", "R"]:
        for player in blocks_base_forward.keys():
            blocks_rating_forward[player] = (
                blocks_base_forward / team_shots_against[teams_dict[player]]
            )


