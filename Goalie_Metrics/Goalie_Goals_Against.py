goalie_goals_against_rating = {}


def goalie_goals_against_get_dict() -> dict:
    return goalie_goals_against_rating


def goalie_goals_against_get_data_set(match_data : dict={}) -> dict:
    goals_against = {}
    for goalie in match_data.keys():
        goals_against_game = match_data[goalie][1]["shots"] - \
            match_data[goalie][1]["saves"]
        goals_against[goalie] = [match_data[goalie][0], goals_against_game]
    return goals_against


def goalie_goals_against_add_match_data(goalie_goals_against_data : dict={}) \
                                                                        -> None:
    for goalie in goalie_goals_against_data.keys():
        if goalie in goalie_goals_against_rating.keys():
            goalie_goals_against_rating[goalie] += \
                goalie_goals_against_data[goalie][1]
        else:
            goalie_goals_against_rating[goalie] = \
                goalie_goals_against_data[goalie][1]


def goalie_goals_against_scale_by_utilization(goalie_utilzation : dict={}) \
                                                                        -> None:
    for goalie in goalie_goals_against_rating.keys():
        goalie_goals_against_rating[goalie] = \
            (goalie_goals_against_rating[goalie] + 1) / \
                goalie_utilzation[goalie]
