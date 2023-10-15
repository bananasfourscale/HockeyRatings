defensemen_discipline_rating = {}

defensemen_penalty_min = {}


def defensemen_discipline_get_dict() -> dict:
    return defensemen_discipline_rating


def defensemen_discipline_reset() -> None:
    defensemen_discipline_rating.clear()
    defensemen_penalty_min.clear()


def defensemen_discipline_get_data(match_data : dict={}) -> dict:

    # loop through all defensemen and populate each type of icetime
    discipline = {}
    for defensemen in match_data.keys():
        try:
            discipline[defensemen] = [
                match_data[defensemen][0],
                match_data[defensemen][1]["penaltyMinutes"]
            ]
        except KeyError:
            discipline[defensemen] = [match_data[defensemen][0], 0]
    return discipline


def defensemen_discipline_add_match_data(defensemen_discipline_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_discipline_data.keys():
        if defensemen in defensemen_penalty_min.keys():
            defensemen_penalty_min[defensemen] += \
                defensemen_discipline_data[defensemen][1]
        else:
            defensemen_penalty_min[defensemen] = \
                defensemen_discipline_data[defensemen][1]
  

def defensemen_discipline_scale_by_utilization(defensemen_utilization : dict={})\
                                                                        -> None:

    # (PIM + 1) * (2 - PlayerUtilizationRating)
    for defensemen in defensemen_penalty_min.keys():
        defensemen_discipline_rating[defensemen] = (
            (defensemen_penalty_min[defensemen] + 1) *
                (2 - defensemen_utilization[defensemen])
        )