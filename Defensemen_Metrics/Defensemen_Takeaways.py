defensemen_takeaways_base = {}

defensemen_takeaways_rating = {}


def defensemen_takeaways_get_dict() -> dict:
    return defensemen_takeaways_rating


def defensemen_takeaways_reset() -> None:
    defensemen_takeaways_base.clear()
    defensemen_takeaways_rating.clear()


def defensemen_takeaways_get_data_set(match_data : dict={}) -> dict:
    takeaways = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        try:
            takeaways[defensemen] = [match_data[defensemen][0],
                (match_data[defensemen][1]["takeaways"] - \
                match_data[defensemen][1]["giveaways"])]
        except KeyError:
            takeaways[defensemen] = [match_data[defensemen][0], 0]
    return takeaways


def defensemen_takeaways_add_match_data(defensemen_takeaways_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_takeaways_data.keys():
        if defensemen in defensemen_takeaways_base.keys():
            defensemen_takeaways_base[defensemen] += \
                defensemen_takeaways_data[defensemen][1]
        else:
            defensemen_takeaways_base[defensemen] = \
                defensemen_takeaways_data[defensemen][1]
            

def defensemen_takeaways_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_takeaways_base.keys():
        if defensemen_takeaways_base[defensemen] > 0:
            defensemen_takeaways_rating[defensemen] = (
                defensemen_takeaways_base[defensemen] *
                    (1 + player_utilization[defensemen])
            )
        else:
            defensemen_takeaways_rating[defensemen] = (
                defensemen_takeaways_base[defensemen] /
                    (1 + player_utilization[defensemen])
            )