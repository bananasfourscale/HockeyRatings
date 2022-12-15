defensemen_points_rating = {}


def defensemen_points_get_dict() -> dict:
    return defensemen_points_rating


def defensemen_points_get_data(active_defensemen : dict={}) -> dict:

    # loop through and populate the time on ice
    for defensemen in active_defensemen.keys():

        # shortcut to access stats more cleanly
        player_stats = active_defensemen[defensemen][0]
        time_per_game = player_stats["timeOnIcePerGame"].split(":")
        defensemen_points_rating[defensemen] = \
            (player_stats["goals"] + player_stats["assists"]) / \
            (float(time_per_game[0]) + (float(time_per_game[1]) / 60))
