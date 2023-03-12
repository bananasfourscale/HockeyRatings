forward_blocks_rating = {}


forward_teams = {}


def forward_blocks_get_dict() -> dict:
    return forward_blocks_rating


def forward_blocks_get_forward_teams_dict() -> dict:
    return forward_teams


def forward_blocks_get_data_set(match_data : dict={}) -> dict:

    # loop through and populate the time on ice
    blocks = {}
    for forward in match_data.keys():
        blocks[forward] = \
            [match_data[forward][0], match_data[forward][1]["blocked"]]
    return blocks
        

def forward_blocks_add_match_data(forward_blocks_data : dict={}) -> None:
    for forward in forward_blocks_data:
        if forward in forward_blocks_rating.keys():
            forward_blocks_rating[forward] += \
                forward_blocks_data[forward][1]
        else:
            forward_blocks_rating[forward] = \
                forward_blocks_data[forward][1]
        forward_teams[forward] = forward_blocks_data[forward][0]


def forward_blocks_scale_by_shots_against(team_shots_against : dict={}) \
                                                                        -> None:
    for forward in forward_blocks_rating.keys():
        forward_blocks_rating[forward] /= \
            (team_shots_against[forward_teams[forward]])
