contribution_base_forward = {}

contribution_rating_forward = {}

contribution_base_defense = {}

contribution_rating_defense = {}


def contributing_games_base_get_dict(position : str="") -> dict:
    if position == "D":
        return contribution_base_defense
    if position in ["C", "L", "R"]:
        return contribution_base_forward
    

def contributing_games_rating_get_dict(position : str="") -> dict:
    if position == "D":
        return contribution_rating_defense
    if position in ["C", "L", "R"]:
        return contribution_rating_forward
    

def contributing_games_reset() -> None:
    contribution_base_forward.reset()
    contribution_rating_forward.reset()
    contribution_base_defense.reset()
    contribution_rating_defense.reset()
    

def contributing_games_get_data_set(match_data : dict={}) -> dict:
    contributing_games = {}
    for player in match_data.keys():
        total_points = (
            match_data[player]['stats']['goals'] +
            match_data[player]['stats']['assists']
        )

        # if they score this game then 1 otherwise 0
        if total_points >= 1:
            contributing_games[player] = {'contributing_games' : 1}
        else:
            contributing_games[player] = {'contributing_games' : 0}
    return contributing_games


def contributing_games_add_match_data(contribution_data : dict={},
    position : str="") -> None:
    for player in contribution_data.keys():
        if position == "D":
            if player in contribution_base_defense.keys():
                contribution_base_defense[player] += \
                    contribution_data[player]['contributing_games']
            else:
                contribution_base_defense[player] = \
                    contribution_data[player]['contributing_games']
        if position in ["C", "L", "R"]:
            if player in contribution_base_forward.keys():
                contribution_base_forward[player] += \
                    contribution_data[player]['contributing_games']
            else:
                contribution_base_forward[player] = \
                    contribution_data[player]['contributing_games']


def contributing_games_scale_by_games(team_games_played : dict={},
    teams_dict : dict={}, position : str="") -> None:
    if position == "D":
        for player in contribution_base_defense.keys():
            contribution_rating_defense[player] = (
                contribution_base_defense /
                team_games_played[teams_dict[player]]
            )
    if position in ["C", "L", "R"]:
        for player in contribution_base_forward.keys():
            contribution_rating_forward[player] = (
                contribution_base_forward /
                team_games_played[teams_dict[player]]
            )