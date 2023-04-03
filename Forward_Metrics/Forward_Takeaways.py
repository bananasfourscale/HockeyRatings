forward_takeaways_rating = {}


forward_teams = {}


def forward_takeaways_get_dict() -> dict:
    return forward_takeaways_rating


def forward_takeaways_get_teams_dict() -> dict:
    return forward_teams


def forward_takeaways_get_data_set(match_data : dict={}) -> dict:
    takeaways = {}

    # loop through and populate the time on ice
    for forward in match_data.keys():
        takeaways[forward] = [match_data[forward][0],
            (match_data[forward][1]["takeaways"] - \
                match_data[forward][1]["giveaways"])]
    return takeaways


def forward_takeaways_add_match_data(forward_takeaways_data : dict={}) \
                                                                        -> None:
    for forward in forward_takeaways_data.keys():
        if forward in forward_takeaways_rating.keys():
            forward_takeaways_rating[forward] += \
                forward_takeaways_data[forward][1]
        else:
            forward_takeaways_rating[forward] = \
                forward_takeaways_data[forward][1]
        forward_teams[forward] = \
            forward_takeaways_data[forward][0]
            

def forward_takeaways_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for forward in forward_takeaways_rating.keys():
        if forward_takeaways_rating[forward] > 0:
            forward_takeaways_rating[forward] *= \
                (1 + player_utilization[forward])
        else:
            forward_takeaways_rating[forward] /= \
                (1 + player_utilization[forward])