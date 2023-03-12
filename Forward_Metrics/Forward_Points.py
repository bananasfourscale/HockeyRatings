forward_points_rating = {}


forward_teams = {}


def forward_points_get_dict() -> dict:
    return forward_points_rating


def forward_points_get_teams_dict() -> dict:
    return forward_teams


def forward_points_get_data_set(match_data : dict={}) -> dict:
    points = {}

    # loop through and populate the time on ice
    for forward in match_data.keys():
        points[forward] = [match_data[forward][0],
            (match_data[forward][1]["goals"] + \
                (match_data[forward][1]["assists"] * 0.75))]
    return points


def forward_points_add_match_data(forward_points_data : dict={}) \
                                                                        -> None:
    for forward in forward_points_data.keys():
        if forward in forward_points_rating.keys():
            forward_points_rating[forward] += \
                forward_points_data[forward][1]
        else:
            forward_points_rating[forward] = \
                forward_points_data[forward][1]
        forward_teams[forward] = \
            forward_points_data[forward][0]
            

def forward_points_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for forward in forward_points_rating.keys():
        forward_points_rating[forward] *= \
            (1 + player_utilization[forward])