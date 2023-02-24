goalie_utilization_rating = {}


goalie_teams = {}


def goalie_utilization_get_dict() -> dict:
    return goalie_utilization_rating


def goalie_utlization_get_goalie_teams_dict() -> dict:
    return goalie_teams


def goalie_utilization_get_data_set(match_data : dict={}) -> dict:
    utilization = {}
    for goalie in match_data.keys():
        time_on_ice = match_data[goalie][1]["timeOnIce"].split(":")
        utilization[goalie] = [
            match_data[goalie][0],
            (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60))
        ]
    return utilization


def goalie_utilization_add_match_data(goalie_utilization_data : dict={}) \
                                                                        -> None:
    for goalie in goalie_utilization_data.keys():
        if goalie in goalie_utilization_rating.keys():
            goalie_utilization_rating[goalie] += \
                goalie_utilization_data[goalie][1]
        else:
            goalie_utilization_rating[goalie] = \
                goalie_utilization_data[goalie][1]
        goalie_teams[goalie] = goalie_utilization_data[goalie][0]


def goalie_utilization_scale_by_game(games_played : dict={}) -> None:
    for goalie in goalie_utilization_rating.keys():
        goalie_utilization_rating[goalie] /= games_played[goalie_teams[goalie]]
