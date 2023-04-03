defensemen_discipline_rating = {}


defensemen_penalty_min = {}


defensemen_time_on_ice = {}


defensemen_games_played ={}


def defensemen_discipline_get_dict() -> dict:
    return defensemen_discipline_rating


def defensemen_discipline_get_data(match_data : dict={}) -> dict:

    # loop through all defensemen and populate each type of icetime
    discipline = {}
    for defensemen in match_data.keys():
        time_on_ice = match_data[defensemen][1]["timeOnIce"].split(":")
        discipline[defensemen] = [
            match_data[defensemen][0],
            match_data[defensemen][1]["penaltyMinutes"],
            float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)
        ]
    return discipline


def defensemen_discipline_add_match_data(defensemen_discipline_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_discipline_data.keys():
        if defensemen in defensemen_penalty_min.keys():
            defensemen_penalty_min[defensemen] += \
                defensemen_discipline_data[defensemen][1]
            defensemen_time_on_ice[defensemen] += \
                defensemen_discipline_data[defensemen][2]
            defensemen_games_played[defensemen] += 1
        else:
            defensemen_penalty_min[defensemen] = \
                defensemen_discipline_data[defensemen][1]
            defensemen_time_on_ice[defensemen] = \
                defensemen_discipline_data[defensemen][2]
            defensemen_games_played[defensemen] = 1
  

def defensemen_discipline_calculate(defensemen_utilization : dict={}) -> None:

    # (PIM + 1) * (2 - PlayerUtilizationRating)
    for defensemen in defensemen_penalty_min.keys():
        defensemen_discipline_rating[defensemen] = \
            (defensemen_penalty_min[defensemen] + 1) * \
            (2 - defensemen_utilization[defensemen])