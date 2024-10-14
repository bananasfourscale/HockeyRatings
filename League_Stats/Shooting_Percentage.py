from Ice_Mapping import zone_to_string, event_point_get_zone

shooting_per_by_zone = {
    "neutral" : 0.0,
    "distance" : 0.0,
    "high_danger" : 0.0,
    "netfront" : 0.0,
    "behind_net": 0.0,
    "corners" : 0.0,
    "outside" : 0.0,
}

shots_by_zone = {
    "neutral" : 0.0,
    "distance" : 0.0,
    "high_danger" : 0.0,
    "netfront" : 0.0,
    "behind_net": 0.0,
    "corners" : 0.0,
    "outside" : 0.0,
}

goals_by_zone = {
    "neutral" : 0.0,
    "distance" : 0.0,
    "high_danger" : 0.0,
    "netfront" : 0.0,
    "behind_net": 0.0,
    "corners" : 0.0,
    "outside" : 0.0,
}

def shooting_percentage_get_shpct_by_zone_get_dict() -> dict:
    return shooting_per_by_zone


def shooting_percentage_get_shots_dict() -> dict:
    return shots_by_zone


def shooting_percentage_get_goals_dict() -> dict:
    return goals_by_zone


def shooting_percentage_add_match_data(shot_plays : list=[],
    goal_plays : list=[]):

    for play in shot_plays:
        event_zone = event_point_get_zone(play["details"]["xCoord"],
            play["details"]["yCoord"])
        shots_by_zone[zone_to_string(event_zone)] += 1
    for play in goal_plays:
        event_zone = event_point_get_zone(play["details"]["xCoord"],
            play["details"]["yCoord"])
        goals_by_zone[zone_to_string(event_zone)] += 1
        shots_by_zone[zone_to_string(event_zone)] += 1


def shooting_percentage_calculate_league_values():
    for zone in shooting_per_by_zone.keys():
        shooting_per_by_zone[zone] = shots_by_zone[zone] / goals_by_zone[zone]


def shooting_percentage_calculate_team_or_player_value(
    play_by_play_game_data : list = [], filter : str=""):

    for play in play_by_play_game_data:
        play_type = play["typeDescKey"]
        if play["dummy"]:
            pass

            
