forward_points_rating = {}


def forward_points_get_dict() -> dict:
    return forward_points_rating


def forward_points_get_data(active_forwards : dict={}) -> dict:

    # loop through and populate the time on ice
    for forward in active_forwards.keys():

        # shortcut to access stats more cleanly
        player_stats = active_forwards[forward][0]
        time_per_game = player_stats["timeOnIce"].split(":")
        forward_points_rating[forward] = \
            (player_stats["goals"] + player_stats["assists"]) / \
            (float(time_per_game[0]) + (float(time_per_game[1]) / 60))
