contribution_base = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}

contribution_rating = {
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
}


def contributing_games_base_get_dict(position : str="") -> dict:
    if position in contribution_base.keys():
        return contribution_base[position]
    return {}
    

def contributing_games_rating_get_dict(position : str="") -> dict:
    if position in contribution_rating.keys():
        return contribution_rating[position]
    return {}
    

def contributing_games_reset() -> None:
    for key in contribution_base.keys():
        contribution_base[key].clear()
    for key in contribution_rating.keys():
        contribution_rating[key].clear()
    

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
    if position not in contribution_base.keys():
        return {}
    for player in contribution_data.keys():
        if player in contribution_base[position].keys():
            contribution_base[position][player] += \
                contribution_data[player]['contributing_games']
        else:
            contribution_base[position][player] = \
                contribution_data[player]['contributing_games']


def contributing_games_scale_by_games(team_games_played : dict={},
    teams_dict : dict={}, position : str="") -> None:
    if position not in contribution_base.keys():
        return
    for player in contribution_base[position].keys():
        contribution_rating[position][player] = (
            contribution_base[position][player] /
            team_games_played[teams_dict[player]]
        )