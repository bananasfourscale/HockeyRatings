defensemen_takeaways_rating = {}


defensemen_teams = {}


def defensemen_takeaways_get_dict() -> dict:
    return defensemen_takeaways_rating


def defensemen_takeaways_get_teams_dict() -> dict:
    return defensemen_teams


def defensemen_takeaways_get_data_set(match_data : dict={}) -> dict:
    takeaways = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        takeaways[defensemen] = [match_data[defensemen][0],
            (match_data[defensemen][1]["takeaways"] - \
                match_data[defensemen][1]["giveaways"])]
    return takeaways


def defensemen_takeaways_add_match_data(defensemen_takeaways_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_takeaways_data.keys():
        if defensemen in defensemen_takeaways_rating.keys():
            defensemen_takeaways_rating[defensemen] += \
                defensemen_takeaways_data[defensemen][1]
        else:
            defensemen_takeaways_rating[defensemen] = \
                defensemen_takeaways_data[defensemen][1]
            defensemen_teams[defensemen] = \
                defensemen_takeaways_data[defensemen][0]
            

def defensemen_takeaways_scale_by_utilization(player_utilization : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_takeaways_rating.keys():
        defensemen_takeaways_rating[defensemen] *= \
            (1 + player_utilization[defensemen])