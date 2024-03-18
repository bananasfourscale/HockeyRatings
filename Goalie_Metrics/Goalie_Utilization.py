goalie_utilization_base = {}

goalie_utilization_rating = {}


def goalie_utilization_get_dict() -> dict:
    return goalie_utilization_rating


def goalie_utilization_reset() -> None:
    goalie_utilization_base.clear()
    goalie_utilization_rating.clear()


def goalie_utilization_get_data_set(match_data : dict={}) -> dict:
    utilization = {}
    for goalie in match_data.keys():
        time_on_ice = match_data[goalie]['stats']["time_on_ice"].split(":")
        utilization[goalie] = {
            'team' : match_data[goalie]['team'],
            "time_on_ice" : 
                (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
        }
    return utilization


def goalie_utilization_add_match_data(goalie_utilization_data : dict={}) \
                                                                        -> None:
    for goalie in goalie_utilization_data.keys():
        if goalie in goalie_utilization_base.keys():
            goalie_utilization_base[goalie] += \
                goalie_utilization_data[goalie]["time_on_ice"]
        else:
            goalie_utilization_base[goalie] = \
                goalie_utilization_data[goalie]["time_on_ice"]


def goalie_utilization_scale_by_game(games_played : dict={},
    goalie_teams_dict : dict={}) -> None:
    for goalie in goalie_utilization_base.keys():
        goalie_utilization_rating[goalie] = (
            goalie_utilization_base[goalie] / 
                games_played[goalie_teams_dict[goalie]]
        )
