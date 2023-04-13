defensemen_blocks_base = {}

defensemen_blocks_rating = {}


def defensemen_blocks_get_dict() -> dict:
    return defensemen_blocks_rating


def defensemen_blocks_get_data_set(match_data : dict={}) -> dict:

    # loop through and populate the time on ice
    blocks = {}
    for defensemen in match_data.keys():
        try:
            blocks[defensemen] = \
                [match_data[defensemen][0],
                match_data[defensemen][1]["blocked"]]
        except KeyError:
            blocks[defensemen] = [match_data[defensemen][0], 0]
    return blocks
        

def defensemen_blocks_add_match_data(defensemen_blocks_data : dict={}) -> None:
    for defensemen in defensemen_blocks_data:
        if defensemen in defensemen_blocks_base.keys():
            defensemen_blocks_base[defensemen] += \
                defensemen_blocks_data[defensemen][1]
        else:
            defensemen_blocks_base[defensemen] = \
                defensemen_blocks_data[defensemen][1]


def defensemen_blocks_scale_by_shots_against(team_shots_against : dict={},
    defensemen_teams_dict : dict={}) -> None:
    for defensemen in defensemen_blocks_base.keys():
        defensemen_blocks_rating[defensemen] = (
            defensemen_blocks_base[defensemen] /
                team_shots_against[defensemen_teams_dict[defensemen]]
        )
