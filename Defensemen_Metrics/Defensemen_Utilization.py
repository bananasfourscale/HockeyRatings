from enum import Enum


defensemen_utilization_rating = {}


defensemen_even_time = {}


defensemen_pp_time = {}


defensemen_pk_time = {}


defensemen_teams = {}


class defensemen_utilization_weights(Enum):
    EVEN_STRENGTH_WEIGHT = 0.75
    PP_STRENGTH_WEIGHT = 0.10
    PK_STRENGTH_WEIGHT = 0.15


def defensemen_utilization_get_dict() -> dict:
    return defensemen_utilization_rating


def defensemen_utilization_get_even_time_dict() -> dict:
    return defensemen_even_time


def defensemen_utilization_get_pp_time_dict() -> dict:
    return defensemen_pp_time


def defensemen_utilization_get_pk_time_dict() -> dict:
    return defensemen_pk_time


def defensemen_utilization_get_teams_dict() -> dict:
    return defensemen_teams


def defensemen_utilization_get_data_set(match_data : dict={}) -> list:
    even_time = {}
    pp_time = {}
    pk_time = {}
    defensemen_team_set = {}

    # loop through all defensemen and populate each type of icetime
    for defensemen in match_data.keys():
        defensemen_team_set[defensemen] = match_data[defensemen][0]
        
        # stats shortcuts
        player_stats = match_data[defensemen][1]

        # even strength time directly gathered
        time_on_ice = player_stats["evenTimeOnIce"].split(":")
        even_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))

        # power play time relative to how many power plays this team gets
        time_on_ice = player_stats["powerPlayTimeOnIce"].split(":")
        pp_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))

        # penalty kill time relative to how many power plays this team gets
        time_on_ice = player_stats["shortHandedTimeOnIce"].split(":")
        pk_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
    return [defensemen_team_set, even_time, pp_time, pk_time]


def defensemen_utilization_add_match_data(defensemen_utilization_data : list=[]) \
                                                                        -> None:
    for defensemen in defensemen_utilization_data[0].keys():
        if defensemen in defensemen_teams.keys():
            defensemen_even_time[defensemen] += \
                defensemen_utilization_data[1][defensemen]
            defensemen_pp_time[defensemen] += \
                defensemen_utilization_data[2][defensemen]
            defensemen_pk_time[defensemen] += \
                defensemen_utilization_data[3][defensemen]
        else:
            defensemen_even_time[defensemen] = \
                defensemen_utilization_data[1][defensemen]
            defensemen_pp_time[defensemen] = \
                defensemen_utilization_data[2][defensemen]
            defensemen_pk_time[defensemen] = \
                defensemen_utilization_data[3][defensemen]
        defensemen_teams[defensemen] = \
            defensemen_utilization_data[0][defensemen]
            

def defensemen_utilization_scale_all(team_games_played : dict={},
    team_power_play : dict={}, team_penalty_kill : dict={}) -> None:
    for defensemen in defensemen_teams.keys():
        defensemen_even_time[defensemen] /= \
            team_games_played[defensemen_teams[defensemen]]
        defensemen_pp_time[defensemen] /= \
            team_power_play[defensemen_teams[defensemen]]
        defensemen_pk_time[defensemen] /= \
            team_penalty_kill[defensemen_teams[defensemen]]

def defensemen_utilization_combine_metrics(metric_list : list=[]) -> None:
    for defensemen in metric_list[0].keys():
        defensemen_utilization_rating[defensemen] = \
            (metric_list[0][defensemen] * \
                defensemen_utilization_weights.EVEN_STRENGTH_WEIGHT.value) + \
            (metric_list[1][defensemen] * \
                defensemen_utilization_weights.PP_STRENGTH_WEIGHT.value) + \
            (metric_list[2][defensemen] * \
                defensemen_utilization_weights.PK_STRENGTH_WEIGHT.value)
