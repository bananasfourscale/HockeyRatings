discipline_base = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
    'T' : {},
}

discipline_rating = {
    'G' : {},
    'D' : {},
    'C' : {},
    'L' : {},
    'R' : {},
    'T' : {},
}


def discipline_base_get_dict(position : str="") -> dict:
    if position in discipline_base.keys():
        return discipline_base[position]
    return {}


def discipline_rating_get_dict(position : str="") -> dict:
    if position in discipline_rating.keys():
        return discipline_rating[position]
    return {}


def discipline_reset() -> None:
    for key in discipline_base.keys():
        discipline_base[key].clear()
    for key in discipline_rating.keys():
        discipline_rating[key].clear()


def discipline_get_data_set(players : dict={}) -> dict:
    discipline = {}
    for player in players.keys():
        discipline[player] = {
            'penalties_taken' : 
                players[player]['stats']['penalty_minutes'],
            'penalties_drawn' : 
                players[player]['stats']['penalty_minutes_drawn']
        }
    return discipline


def discipline_get_team_data_set(match_data : dict={}) -> dict:
    discipline = {}
    team_list = [match_data['game_stats']['home_team'],
        match_data['game_stats']['away_team']]
    for team in team_list:
        discipline[team] = {
            'penalties_taken' : 
                match_data['game_stats'][team]["team_stats"]['penalty_minutes'],
            'penalties_drawn' :
                match_data['game_stats'][team]["team_stats"]['penalties_drawn']
        }
    return discipline


def discipline_add_match_data(discipline_data : dict = {}, position : str="") \
                                                                        -> None:
    if position not in discipline_base.keys():
        return {}
    for player in discipline_data.keys():
        if player in discipline_base[position].keys():
            discipline_base[position][player] += \
                discipline_data[player]["penalty_net_minutes"]
        else:
            discipline_base[position][player] = \
                discipline_data[player]["penalty_net_minutes"]
                

def discipline_scale_by_utilization(utilization : dict={}, position : str="")\
                                                                        -> None:
    if position not in discipline_base.keys():
        return
    for player in discipline_base[position].keys():
        discipline_rating[position][player] = (
            discipline_base[position][player] * (1 - utilization[player])
        )
