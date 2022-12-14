goalie_save_percentage_rating = {}


def goalie_save_percentage_get_dict() -> dict:
    return goalie_save_percentage_rating


def goalie_save_percentage_get_data(active_goalies : dict={}) -> list:
    even_strength_sp = {}
    power_play_sp = {}
    penalty_kill_sp = {}

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():

        # shortcut to access stats more cleanly
        player_stats = active_goalies[goalie][0]

        # get even strength data
        even_strength_sp[goalie] = player_stats["evenStrengthSavePercentage"]

        # get powerplay data if it exist (own team short handed)
        if player_stats["powerPlayShots"] > 0:
            power_play_sp[goalie] = player_stats["powerPlaySavePercentage"]
        else:
            power_play_sp[goalie] = 100.0

        # get short handed data if it exist (own team power play)
        if player_stats["shortHandedShots"] > 0:
            penalty_kill_sp[goalie] = player_stats["shortHandedSavePercentage"]
        else:
            penalty_kill_sp[goalie] = 100.0
    return [even_strength_sp, power_play_sp, penalty_kill_sp]


def goalie_save_percentage_scale_for_volume(metric_list : list=[],
                                            active_goalies : dict={}) -> list:
    for goalie in metric_list[0].keys():

        # shortcut to access stats more cleanly
        player_stats = active_goalies[goalie][0]

        # (S%_ev / 100) * S_ev
        # (S%_pp / 100) * S_pp
        # (S%_sh / 100) * S_sh
        metric_list[0][goalie] = (metric_list[0][goalie] / 100) * \
            player_stats['evenSaves']
        metric_list[1][goalie] = (metric_list[1][goalie] / 100) * \
            player_stats['powerPlaySaves']
        metric_list[2][goalie] = (metric_list[2][goalie] / 100) * \
            player_stats['shortHandedSaves']
    return metric_list



def goalie_save_percentage_combine_metrics(metric_list : list=[],
    active_goalies : dict={}, all_team_stats : dict={}) -> None:
    
    # unlike other stats which use a flat weight. Have this weight scale so that
    # roughly the percentage of time at each strength is the percent weight.
    # This is designed to be applied after some other corrections but can be
    # applied proactively as well
    for goalie in metric_list[0].keys():
        team_stats = all_team_stats[active_goalies[goalie][1]]

        # get roughly the total ice time for the team of this goalie
        games_played = team_stats["gamesPlayed"]
        total_ice_time = games_played * 60

        # now calculate the percentage of time on the power play, meaning all
        # saves are short handed. Use this as short handed weight
        pp_time = team_stats["powerPlayOpportunities"] * 2
        short_handed_sp_weight = pp_time / total_ice_time

        # now with less available stats in the api do a more roundabout way to
        # get the time on the penalty kill which will become the pp weight
        sh_chances = round(team_stats["powerPlayGoalsAgainst"] / \
            team_stats["powerPlayGoalsAgainst"])
        sh_time = sh_chances * 2
        power_play_sp_weight = sh_time / total_ice_time

        # now the even strength must just be the remainder
        even_strength_sp_weight = (total_ice_time - (sh_time + pp_time)) / \
            total_ice_time
        goalie_save_percentage_rating[goalie] = \
            (metric_list[0][goalie] * even_strength_sp_weight) + \
            (metric_list[1][goalie] * power_play_sp_weight) + \
            (metric_list[2][goalie] * short_handed_sp_weight)
