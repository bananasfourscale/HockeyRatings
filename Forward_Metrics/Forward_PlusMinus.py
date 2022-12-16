forward_plus_minus_rating = {}


def forward_plus_minus_get_dict() -> dict:
    return forward_plus_minus_rating


def forward_plus_minus_get_data(active_forwards : dict={}) -> dict:

    # loop through and populate the time on ice
    for forward in active_forwards.keys():

        # shortcut to access stats more cleanly
        player_stats = active_forwards[forward][0]
        time_per_game = player_stats["timeOnIcePerGame"].split(":")
        forward_plus_minus_rating[forward] = player_stats["plusMinus"] + \
            (float(time_per_game[0]) + (float(time_per_game[1]) / 60))
