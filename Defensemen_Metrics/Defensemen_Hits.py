defensemen_hits_rating = {}


def defensemen_hits_get_dict() -> dict:
    return defensemen_hits_rating


def defensemen_hits_get_data(active_defensemen : dict={}) -> dict:

    # loop through and populate the time on ice
    for defensemen in active_defensemen.keys():

        # shortcut to access stats more cleanly
        player_stats = active_defensemen[defensemen][0]
        defensemen_hits_rating[defensemen] = player_stats["hits"]
