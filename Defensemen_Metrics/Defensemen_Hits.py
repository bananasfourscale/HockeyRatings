defensemen_hits_rating = {}


defensemen_teams = {}


def defensemen_hits_get_dict() -> dict:
    return defensemen_hits_rating


def defensemen_hits_get_teams_dict() -> dict:
    return defensemen_teams


def defensemen_hits_get_data_set(match_data : dict={}) -> dict:
    hits = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        hits[defensemen] = \
            [match_data[defensemen][0], match_data[defensemen][1]["hits"]]
    return hits


def defensemen_hits_add_match_data(defensemen_hits_data : dict={}) -> None:
    for defensemen in defensemen_hits_data.keys():
        if defensemen in defensemen_hits_rating.keys():
            defensemen_hits_rating[defensemen] += \
                defensemen_hits_data[defensemen][1]
        else:
            defensemen_hits_rating[defensemen] = \
                defensemen_hits_data[defensemen][1]
        defensemen_teams[defensemen] = defensemen_hits_data[defensemen][0]


def defensemen_hits_scale_by_games(player_utilization : dict={}) -> None:
    for defensemen in defensemen_hits_rating.keys():
        defensemen_hits_rating[defensemen] *= \
            (1 + player_utilization[defensemen])