from enum import Enum


defensemen_utilization_rating = {}


class defensemen_utilization_weights(Enum):
    EVEN_STRENGTH_WEIGHT = 0.75
    PP_STRENGTH_WEIGHT = 0.10
    PK_STRENGTH_WEIGHT = 0.15


def defensemen_utilization_get_dict() -> dict:
    return defensemen_utilization_rating


def defensemen_utilization_get_data(active_defensemen : dict={},
                                    all_team_stats : dict={}) -> list:
    even_time = {}
    pp_time = {}
    pk_time = {}

    # loop through all defensemen and populate each type of icetime
    for defensemen in active_defensemen.keys():
        
        # stats shortcuts
        player_stats = active_defensemen[defensemen][0]
        team_stats = all_team_stats[active_defensemen[defensemen][1]]

        # even strength time directly gathered
        time_on_ice = player_stats["evenTimeOnIce"].split(":")
        even_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            (team_stats["gamesPlayed"] * 60)

        # power play time relative to how many power plays this team gets
        time_on_ice = player_stats["powerPlayTimeOnIce"].split(":")
        pp_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            (team_stats["powerPlayOpportunities"] * 2)

        # penalty kill time relative to how many power plays this team gets
        time_on_ice = player_stats["shortHandedTimeOnIce"].split(":")
        pk_time[defensemen] = \
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
            ((team_stats["powerPlayGoalsAgainst"] /
            (1 - (float(team_stats["penaltyKillPercentage"]) / 100))) * 2)
    return [even_time, pp_time, pk_time]


def defensemen_utilization_combine_metrics(metric_list : list=[]) -> None:
    for defensemen in metric_list[0].keys():
        defensemen_utilization_rating[defensemen] = \
            (metric_list[0][defensemen] * \
                defensemen_utilization_weights.EVEN_STRENGTH_WEIGHT.value) + \
            (metric_list[1][defensemen] * \
                defensemen_utilization_weights.PP_STRENGTH_WEIGHT.value) + \
            (metric_list[2][defensemen] * \
                defensemen_utilization_weights.PK_STRENGTH_WEIGHT.value)
