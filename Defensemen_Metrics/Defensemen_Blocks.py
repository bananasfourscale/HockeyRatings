defensemen_blocks_rating = {}


defensemen_teams = {}


def defensemen_blocks_get_dict() -> dict:
    return defensemen_blocks_rating


def defensemen_blocks_get_defensemen_teams_dict() -> dict:
    return defensemen_teams


def defensemen_blocks_get_data_set(match_data : dict={}) -> dict:

    # loop through and populate the time on ice
    blocks = {}
    for defensemen in match_data.keys():
        blocks[defensemen] = \
            [match_data[defensemen][0], match_data[defensemen][1]["blocked"]]
    return blocks
        

def defensemen_blocks_add_match_data(defensemen_blocks_data : dict={}) -> None:
    for defensemen in defensemen_blocks_data:
        if defensemen in defensemen_blocks_rating.keys():
            defensemen_blocks_rating[defensemen] += \
                defensemen_blocks_data[defensemen][1]
        else:
            defensemen_blocks_rating[defensemen] = \
                defensemen_blocks_data[defensemen][1]
            defensemen_teams[defensemen] = defensemen_blocks_data[defensemen][0]


def defensemen_blocks_scale_by_shots_against(team_shots_against : dict={}) \
                                                                        -> None:
    for defensemen in defensemen_blocks_rating.keys():
        defensemen_blocks_rating[defensemen] /= \
            (team_shots_against[defensemen_teams[defensemen]])
