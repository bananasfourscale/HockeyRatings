clutch_rating_base = {}

clutch_games_played = {}

clutch_rating = {}

clutch_trends = {}


def clutch_rating_get_dict() -> dict:
    return clutch_rating


def clutch_rating_get_trend_dict() -> dict:
    return clutch_trends


def clutch_get_lead_data(match_data : dict={}) -> dict:
    
    # loop through the lines of file
    win_lead_first = {}
    win_lead_second = {}

    # home team data
    home_team = match_data['linescore']["teams"]["home"]["team"]["name"]
    home_score_first = match_data['linescore']["linescore"]["periods"][0][
        "home"]["goals"]
    home_score_second = \
        match_data['linescore']["linescore"]["periods"][1]["home"]["goals"] + \
        home_score_first
    home_score_final = match_data['linescore']["teams"]["home"]["score"]

    # away team data    
    away_team = match_data['linescore']["teams"]["away"]["team"]["name"]
    away_score_first = match_data['linescore']["linescore"]["periods"][0][
        "away"]["goals"]
    away_score_second = \
        match_data['linescore']["linescore"]["periods"][1]["away"]["goals"] + \
        away_score_first
    away_score_final = match_data['linescore']["teams"]["away"]["score"]

    # set default values
    win_lead_first[home_team] = [0,0]
    win_lead_first[away_team] = [0,0]
    win_lead_second[home_team] = [0,0]
    win_lead_second[away_team] = [0,0]

    # determine who was leading after one period
    if away_score_first > home_score_first:
        if away_score_final > home_score_final:
            win_lead_first[away_team] = [1,1]
        else:
            win_lead_first[away_team] = [0,1]
    elif home_score_first > away_score_first:
        if home_score_final > away_score_final:
            win_lead_first[home_team] = [1,1]
        else:
            win_lead_first[home_team] = [0,1]

    # if teams are tied them give them both full marks
    else:
        win_lead_first[away_team] = [1,1]
        win_lead_first[home_team] = [1,1]
    
    # now do the same for the second period
    if away_score_second > home_score_second:
        if away_score_final > home_score_final:
            win_lead_second[away_team] = [1,1]
        else:
            win_lead_second[away_team] = [0,1]
    elif home_score_second > away_score_second:
        if home_score_final > away_score_final:
            win_lead_second[home_team] = [1,1]
        else:
            win_lead_second[home_team] = [0,1]

    # if teams are tied them give them both full marks
    else:
        win_lead_second[away_team] = [1,1]
        win_lead_second[home_team] = [1,1]

    # collect all the different permutations into one data set and return
    clutch_lead_data = {}
    for team in win_lead_first.keys():
        clutch_lead_data[team] = [win_lead_first[team], win_lead_second[team]]
    return clutch_lead_data


def clutch_calculate_lead_protection(match_data : dict={}) -> None:
    clutch_data = {}
    lead_protection_data = clutch_get_lead_data(match_data)
    for team in lead_protection_data.keys():

        # lead protection first period
        if lead_protection_data[team][0][1] == 0:
            win_lead_first_per = 0.0
        else:
            win_lead_first_per = lead_protection_data[team][0][0] / \
                lead_protection_data[team][0][1]

        # lead protection second period
        if lead_protection_data[team][1][1] == 0:
            win_lead_second_per = 0.0
        else:
            win_lead_second_per = lead_protection_data[team][1][0] / \
                lead_protection_data[team][1][1]
        clutch_data[team] = (win_lead_first_per) + (win_lead_second_per * 2)
    return clutch_data


def clutch_add_match_data(clutch_data : dict={}) -> None:
    for team in clutch_data.keys():
        if team in clutch_rating_base.keys():
            clutch_rating_base[team] += clutch_data[team]
            clutch_games_played[team] += 1
        else:
            clutch_rating_base[team] = clutch_data[team]
            clutch_games_played[team] = 1


def clutch_rating_scale_by_game() -> None:
    for team in clutch_rating_base.keys():
        clutch_rating[team] = (
            clutch_rating_base[team] / clutch_games_played[team]
        )


def clutch_update_trend(date : str="") -> None:
    clutch_trends[date] = {}
    for team in clutch_rating.keys():
        clutch_trends[date][team] = clutch_rating[team]
