from enum import Enum


forward_utilization_rating = {}


class forward_utilization_weights(Enum):
    EVEN_STRENGTH_WEIGHT = 0.75
    PP_STRENGTH_WEIGHT = 0.15
    PK_STRENGTH_WEIGHT = 0.10


def forward_utilization_get_dict() -> dict:
    return forward_utilization_rating


def forward_utilization_get_data(active_forwards : dict={},
                                 all_team_stats : dict={}) -> list:
    even_time = {}
    pp_time = {}
    pk_time = {}

    # loop through all forward and populate each type of icetime
    for forward in active_forwards.keys():
        
        # stats shortcuts
        player_stats = active_forwards[forward][0]
        team_stats = all_team_stats[active_forwards[forward][1]]

        # even strength time directly gathered
        time_on_ice = player_stats["evenTimeOnIce"].split(":")
        even_time[forward] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            (team_stats["gamesPlayed"] * 60)

        # power play time relative to how many power plays this team gets
        time_on_ice = player_stats["powerPlayTimeOnIce"].split(":")
        pp_time[forward] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            (team_stats["powerPlayOpportunities"] * 2)

        # penalty kill time relative to how many power plays this team gets
        time_on_ice = player_stats["shortHandedTimeOnIce"].split(":")
        pk_time[forward] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            ((team_stats["powerPlayGoalsAgainst"] /
            (1 - (float(team_stats["penaltyKillPercentage"]) / 100))) * 2)
    return [even_time, pp_time, pk_time]


def forward_utilization_combine_metrics(metric_list : list=[]) -> None:
    for forward in metric_list[0].keys():
        forward_utilization_rating[forward] = \
            (metric_list[0][forward] * \
                forward_utilization_weights.EVEN_STRENGTH_WEIGHT.value) + \
            (metric_list[1][forward] * \
                forward_utilization_weights.PP_STRENGTH_WEIGHT.value) + \
            (metric_list[2][forward] * \
                forward_utilization_weights.PK_STRENGTH_WEIGHT.value)
