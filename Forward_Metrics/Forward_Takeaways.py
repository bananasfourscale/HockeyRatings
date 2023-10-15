forward_takeaway_base = {}

forward_takeaways_rating = {}


def forward_takeaways_get_dict() -> dict:
    return forward_takeaways_rating


def forward_takeaways_reset() -> None:
    forward_takeaway_base.clear()
    forward_takeaways_rating.clear()


def forward_takeaways_get_data_set(match_data : dict={}) -> dict:
    takeaways = {}

    # loop through and populate the time on ice
    for forward in match_data.keys():
        try:
            takeaways[forward] = [match_data[forward][0],
                (match_data[forward][1]["takeaways"] - \
                match_data[forward][1]["giveaways"])]
        except KeyError:
            takeaways[forward] = [match_data[forward][0], 0]
    return takeaways


def forward_takeaways_add_match_data(forward_takeaways_data : dict={}) \
                                                                        -> None:
    for forward in forward_takeaways_data.keys():
        if forward in forward_takeaway_base.keys():
            forward_takeaway_base[forward] += \
                forward_takeaways_data[forward][1]
        else:
            forward_takeaway_base[forward] = \
                forward_takeaways_data[forward][1]
            

def forward_takeaways_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for forward in forward_takeaway_base.keys():
        if forward_takeaway_base[forward] > 0:
            forward_takeaways_rating[forward] = (
                forward_takeaway_base[forward] *
                    (1 + player_utilization[forward])
            )
        else:
            forward_takeaways_rating[forward] = (
                forward_takeaway_base[forward] /
                    (1 + player_utilization[forward])
            )