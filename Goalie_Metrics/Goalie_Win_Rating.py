import requests
import json


goalie_win_rating = {}


def goalie_win_rating_get_dict() -> dict:
    return goalie_win_rating


def goalie_win_rating_calculate(active_goalies : dict={}) -> None:

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():

        # shortcut to access stats more cleanly
        player_stats = active_goalies[goalie][0]

        # (W * 1) + (OTL * .33)
        wins = player_stats["wins"]
        ot_losses = player_stats["ot"]
        shutouts = player_stats["shutouts"]
        goalie_win_rating[goalie] = (wins) + (ot_losses * 0.33) + \
            (shutouts * 0.1)
