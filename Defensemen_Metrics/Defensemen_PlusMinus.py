defensemen_plus_minus_rating = {}


def defensemen_plus_minus_get_dict() -> dict:
    return defensemen_plus_minus_rating


def defensemen_plus_minus_get_data(active_defensemen : dict={}) -> dict:

    # loop through and populate the time on ice
    for defensemen in active_defensemen.keys():

        # shortcut to access stats more cleanly
        player_stats = active_defensemen[defensemen][0]
        time_per_game = player_stats["timeOnIcePerGame"].split(":")
        defensemen_plus_minus_rating[defensemen] = player_stats["plusMinus"] + \
            (float(time_per_game[0]) + (float(time_per_game[1]) / 60))
