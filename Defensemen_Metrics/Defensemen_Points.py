defensemen_points_base = {}

defensemen_points_rating = {}


def defensemen_points_get_dict() -> dict:
    return defensemen_points_rating


def defensemen_points_reset() -> None:
    defensemen_points_base.clear()
    defensemen_points_rating.clear()


def defensemen_points_get_data_set(match_data : dict={}) -> dict:
    points = {}

    # loop through and populate the time on ice
    for defensemen in match_data.keys():
        points[defensemen] = [match_data[defensemen][0],
            (match_data[defensemen][1]["goals"] + \
                (match_data[defensemen][1]["assists"] * 0.90))]
    return points


def defensemen_points_add_match_data(defensemen_points_data : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_points_data.keys():
        if defensemen in defensemen_points_base.keys():
            defensemen_points_base[defensemen] += \
                defensemen_points_data[defensemen][1]
        else:
            defensemen_points_base[defensemen] = \
                defensemen_points_data[defensemen][1]
            

def defensemen_points_scale_by_games(teams_games_played : dict={},
    defensemen_teams_dict : dict={}) -> None:
    for defensemen in defensemen_points_base.keys():
        defensemen_points_rating[defensemen] = (
            defensemen_points_base[defensemen] /
                teams_games_played[defensemen_teams_dict[defensemen]]
        )