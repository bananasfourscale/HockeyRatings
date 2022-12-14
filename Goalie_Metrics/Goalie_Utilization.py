import requests
import json


goalie_utilization_rating = {}


def goalie_utilization_get_dict() -> dict:
    return goalie_utilization_rating


def goalie_utilization_calculate_time_on_ice(active_goalies : dict={},
                                             all_team_stats : dict={}) -> None:

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():

        # shortcut to access stats more cleanly
        player_stats = active_goalies[goalie][0]
        team_stats = all_team_stats[active_goalies[goalie][1]]

        # ((TOIm + (TOIs / 60))) / TeamGP
        time_on_ice = player_stats["timeOnIce"].split(":")
        goalie_utilization_rating[goalie] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
                team_stats["gamesPlayed"]
