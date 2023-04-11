forward_discipline_rating = {}


forward_penalty_min = {}


forward_time_on_ice = {}


forward_games_played ={}


def forward_discipline_get_dict() -> dict:
    return forward_discipline_rating


def forward_discipline_get_data(match_data : dict={}) -> dict:

    # loop through all forward and populate each type of icetime
    discipline = {}
    for forward in match_data.keys():
        time_on_ice = match_data[forward][1]["timeOnIce"].split(":")
        try:
            discipline[forward] = [
                match_data[forward][0],
                match_data[forward][1]["penaltyMinutes"],
                float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)]
        except KeyError:
            discipline[forward] = [match_data[forward][0], 0,
                float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)]
    return discipline


def forward_discipline_add_match_data(forward_discipline_data : dict={}) \
                                                                        -> None:
    for forward in forward_discipline_data.keys():
        if forward in forward_penalty_min.keys():
            forward_penalty_min[forward] += \
                forward_discipline_data[forward][1]
            forward_time_on_ice[forward] += \
                forward_discipline_data[forward][2]
            forward_games_played[forward] += 1
        else:
            forward_penalty_min[forward] = \
                forward_discipline_data[forward][1]
            forward_time_on_ice[forward] = \
                forward_discipline_data[forward][2]
            forward_games_played[forward] = 1
  

def forward_discipline_scale_by_utilization(forward_utilization : dict={}) \
                                                                        -> None:

    # (PIM + 1) * (2 - PlayerUtilizationRating)
    for forward in forward_penalty_min.keys():
        forward_discipline_rating[forward] = \
            (forward_penalty_min[forward] + 1) * \
            (2 - forward_utilization[forward])