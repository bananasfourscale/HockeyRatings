import requests
import json


goalie_goals_against_rating = {}


def goalie_goals_against_get_dict() -> dict:
    return goalie_goals_against_rating


def goalie_goals_against_get_data(active_goalies : dict={}) -> dict:

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():

        # shortcut to access stats more cleanly
        player_stats = active_goalies[goalie][0]
        goalie_goals_against_rating[goalie] = player_stats["goalAgainstAverage"]
