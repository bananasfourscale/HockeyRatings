forward_hits_rating = {}


forward_teams = {}


def forward_hits_get_dict() -> dict:
    return forward_hits_rating


def forward_hits_get_teams_dict() -> dict:
    return forward_teams


def forward_hits_get_data_set(match_data : dict={}) -> dict:
    hits = {}

    # loop through and populate the time on ice
    for forward in match_data.keys():
        hits[forward] = \
            [match_data[forward][0], match_data[forward][1]["hits"]]
    return hits


def forward_hits_add_match_data(forward_hits_data : dict={}) -> None:
    for forward in forward_hits_data.keys():
        if forward in forward_hits_rating.keys():
            forward_hits_rating[forward] += \
                forward_hits_data[forward][1]
        else:
            forward_hits_rating[forward] = \
                forward_hits_data[forward][1]
        forward_teams[forward] = forward_hits_data[forward][0]


def forward_hits_scale_by_games(player_utilization : dict={}) -> None:
    for forward in forward_hits_rating.keys():
        forward_hits_rating[forward] *= \
            (1 + player_utilization[forward])