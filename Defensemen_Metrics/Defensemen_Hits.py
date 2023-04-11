defensemen_hits_rating = {}


def defensemen_hits_get_dict() -> dict:
    return defensemen_hits_rating


def defensemen_hits_get_data_set(match_data : dict={}) -> dict:
    hits = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        try:
            hits[defensemen] = \
                [match_data[defensemen][0], match_data[defensemen][1]["hits"]]
        except KeyError:
            hits[defensemen] = [match_data[defensemen][0], 0]
    return hits


def defensemen_hits_add_match_data(defensemen_hits_data : dict={}) -> None:
    for defensemen in defensemen_hits_data.keys():
        if defensemen in defensemen_hits_rating.keys():
            defensemen_hits_rating[defensemen] += \
                defensemen_hits_data[defensemen][1]
        else:
            defensemen_hits_rating[defensemen] = \
                defensemen_hits_data[defensemen][1]


def defensemen_hits_scale_by_games(teams_games_played : dict={},
    defensemen_teams_dict : dict={}) -> None:
    for defensemen in defensemen_hits_rating.keys():
        defensemen_hits_rating[defensemen] /= \
            teams_games_played[defensemen_teams_dict[defensemen]]