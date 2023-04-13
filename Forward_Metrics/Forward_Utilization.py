from enum import Enum

forward_even_base = {}

forward_even_time = {}

forward_pp_base = {}

forward_pp_time = {}

forward_pk_base = {}

forward_pk_time = {}

forward_utilization_rating = {}


class forward_utilization_weights(Enum):
    EVEN_STRENGTH_WEIGHT = 0.75
    PP_STRENGTH_WEIGHT = 0.15
    PK_STRENGTH_WEIGHT = 0.10


def forward_utilization_get_dict() -> dict:
    return forward_utilization_rating


def forward_utilization_get_even_time_dict() -> dict:
    return forward_even_time


def forward_utilization_get_pp_time_dict() -> dict:
    return forward_pp_time


def forward_utilization_get_pk_time_dict() -> dict:
    return forward_pk_time


def forward_utilization_get_data_set(match_data : dict={}) -> list:
    even_time = {}
    pp_time = {}
    pk_time = {}
    forward_team_set = {}

    # loop through all forward and populate each type of icetime
    for forward in match_data.keys():
        forward_team_set[forward] = match_data[forward][0]
        
        # stats shortcuts
        player_stats = match_data[forward][1]
        try:

            # even strength time directly gathered
            time_on_ice = player_stats["evenTimeOnIce"].split(":")
            even_time[forward] = \
                (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))

            # power play time relative to how many power plays this team gets
            time_on_ice = player_stats["powerPlayTimeOnIce"].split(":")
            pp_time[forward] = \
                (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))

            # penalty kill time relative to how many power plays this team gets
            time_on_ice = player_stats["shortHandedTimeOnIce"].split(":")
            pk_time[forward] = \
                (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
        except KeyError:
            time_on_ice = player_stats["timeOnIce"].split(":")
            if float(time_on_ice[0]) == 0:
                even_time[forward] = 0
                pp_time[forward] = 0
                pk_time[forward] = 0
            else:
                even_time[forward] = \
                    (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
                pp_time[forward] = \
                    (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
                pk_time[forward] = \
                    (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
    return [forward_team_set, even_time, pp_time, pk_time]


def forward_utilization_add_match_data(forward_utilization_data : list=[]) \
                                                                        -> None:
    for forward in forward_utilization_data[0].keys():
        if forward in forward_even_base.keys():
            forward_even_base[forward] += \
                forward_utilization_data[1][forward]
            forward_pp_base[forward] += \
                forward_utilization_data[2][forward]
            forward_pk_base[forward] += \
                forward_utilization_data[3][forward]
        else:
            forward_even_base[forward] = \
                forward_utilization_data[1][forward]
            forward_pp_base[forward] = \
                forward_utilization_data[2][forward]
            forward_pk_base[forward] = \
                forward_utilization_data[3][forward]
            

def forward_utilization_scale_all(team_games_played : dict={},
    team_power_play : dict={}, team_penalty_kill : dict={},
    forward_teams_dict : dict={}) -> None:
    for forward in forward_teams_dict.keys():
        forward_even_time[forward] = (
            forward_even_base[forward] /
                team_games_played[forward_teams_dict[forward]]
        )
        if team_power_play[forward_teams_dict[forward]] > 0:
            forward_pp_time[forward] = (
                forward_pp_base[forward] /
                    team_power_play[forward_teams_dict[forward]]
            )
        else:
            forward_pp_time[forward] = 0

        if team_penalty_kill[forward_teams_dict[forward]] > 0:
            forward_pk_time[forward] = (
                forward_pk_base[forward] /
                    team_penalty_kill[forward_teams_dict[forward]]
            )
        else:
            forward_pk_time[forward] = 0


def forward_utilization_combine_metrics() -> None:
    for forward in forward_even_time.keys():
        forward_utilization_rating[forward] = (
            (forward_even_time[forward] *
                forward_utilization_weights.EVEN_STRENGTH_WEIGHT.value) +
            (forward_pp_time[forward] *
                forward_utilization_weights.PP_STRENGTH_WEIGHT.value) +
            (forward_pk_time[forward] *
                forward_utilization_weights.PK_STRENGTH_WEIGHT.value)
        )
