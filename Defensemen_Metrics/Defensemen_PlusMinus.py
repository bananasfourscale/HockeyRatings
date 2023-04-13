defensemen_plus_minus_base = {}

defensemen_plus_minus_rating = {}


def defensemen_plus_minus_get_dict() -> dict:
    return defensemen_plus_minus_rating


def defensemen_plus_minus_get_data_set(match_data : dict={}) -> dict:
    plus_minus = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        try:
            plus_minus[defensemen] = [match_data[defensemen][0],
                match_data[defensemen][1]["plusMinus"]]
        except KeyError:
            plus_minus[defensemen] = [match_data[defensemen][0], 0]
    return plus_minus


def defensemen_plus_minus_add_match_data(defensemen_plus_minus_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_plus_minus_data.keys():
        if defensemen in defensemen_plus_minus_base.keys():
            defensemen_plus_minus_base[defensemen] += \
                defensemen_plus_minus_data[defensemen][1]
        else:
            defensemen_plus_minus_base[defensemen] = \
                defensemen_plus_minus_data[defensemen][1]
            

def defensemen_plus_minus_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_plus_minus_base.keys():
        if defensemen_plus_minus_base[defensemen] > 0:
            defensemen_plus_minus_rating[defensemen] = (
                defensemen_plus_minus_base[defensemen] *
                    (1 + player_utilization[defensemen])
            )
        else:
            defensemen_plus_minus_rating[defensemen] = (
                defensemen_plus_minus_base[defensemen] /
                    (1 + player_utilization[defensemen])
            )
