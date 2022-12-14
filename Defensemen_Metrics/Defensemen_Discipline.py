defensemen_discipline_rating = {}


def defensemen_discipline_get_dict() -> dict:
    return defensemen_discipline_rating


def defensemen_discipline_get_data(active_defensemen : dict={}) -> dict:

    # loop through all defensemen and populate each type of icetime
    for defensemen in active_defensemen.keys():
        player_stats = active_defensemen[defensemen][0]
        time_on_ice = player_stats["timeOnIce"].split(":")
        defensemen_discipline_rating[defensemen] = player_stats["pim"] / \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))

        