forward_plus_minus_rating = {}


def forward_plus_minus_get_dict() -> dict:
    return forward_plus_minus_rating


def forward_plus_minus_get_data_set(match_data : dict={}) -> dict:
    plus_minus = {}

    # loop through and populate the time on ice
    for forward in match_data.keys():
        plus_minus[forward] = [match_data[forward][0],
            match_data[forward][1]["plusMinus"]]
    return plus_minus


def forward_plus_minus_add_match_data(forward_plus_minus_data : dict={}) \
                                                                        -> None:
    for forward in forward_plus_minus_data.keys():
        if forward in forward_plus_minus_rating.keys():
            forward_plus_minus_rating[forward] += \
                forward_plus_minus_data[forward][1]
        else:
            forward_plus_minus_rating[forward] = \
                forward_plus_minus_data[forward][1]
            

def forward_plus_minus_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for forward in forward_plus_minus_rating.keys():
        if forward_plus_minus_rating[forward] > 0:
            forward_plus_minus_rating[forward] *= \
                (1 + player_utilization[forward])
        else:
            forward_plus_minus_rating[forward] /= \
                (1 + player_utilization[forward])