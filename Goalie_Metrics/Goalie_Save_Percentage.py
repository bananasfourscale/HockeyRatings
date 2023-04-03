goalie_save_percentage_rating = {}


goalie_even_save = {}


goalie_pp_save = {}


goalie_sh_save = {}


def goalie_save_percentage_get_dict() -> dict:
    return goalie_save_percentage_rating


def goalie_save_percentage_get_data_set(match_data : dict={}) -> list:
    even_strength_sp = {}
    power_play_sp = {}
    penalty_kill_sp = {}
    goalie_teams_set = {}

    # loop through and populate the time on ice
    for goalie in match_data.keys():
        goalie_teams_set[goalie] = match_data[goalie][0]

        # get even strength data
        even_strength_sp[goalie] = [
            match_data[goalie][1]["evenSaves"]**2,
            match_data[goalie][1]["evenShotsAgainst"]
        ]

        # get powerplay data if it exist (own team short handed)
        if match_data[goalie][1]["powerPlayShotsAgainst"] > 0:
            power_play_sp[goalie] = [
            match_data[goalie][1]["powerPlaySaves"]**2,
            match_data[goalie][1]["powerPlayShotsAgainst"]
        ]
        else:
            power_play_sp[goalie] = [0,0]

        # get short handed data if it exist (own team power play)
        if match_data[goalie][1]["shortHandedShotsAgainst"] > 0:
            penalty_kill_sp[goalie] = [
            match_data[goalie][1]["shortHandedSaves"]**2,
            match_data[goalie][1]["shortHandedShotsAgainst"]
        ]
        else:
            penalty_kill_sp[goalie] = [0,0]
    return [goalie_teams_set, even_strength_sp, power_play_sp, penalty_kill_sp]


def goalie_save_percentage_add_match_data(goalie_save_percentage_data : dict={})\
                                                                        -> None:
    goalie_teams_set = goalie_save_percentage_data[0]
    goalie_even = goalie_save_percentage_data[1]
    goalie_pp = goalie_save_percentage_data[2]
    goalie_sh = goalie_save_percentage_data[3]
    for goalie in goalie_save_percentage_data[0].keys():

        # even strength
        if goalie in goalie_even_save.keys():
            goalie_even_save[goalie][0] += goalie_even[goalie][0]
            goalie_even_save[goalie][1] += goalie_even[goalie][1]
        else:
            goalie_even_save[goalie] = goalie_even[goalie]
            goalie_even_save[goalie] = goalie_even[goalie]

        # pp strengths
        if goalie in goalie_pp_save.keys():
            goalie_pp_save[goalie][0] += goalie_pp[goalie][0]
            goalie_pp_save[goalie][1] += goalie_pp[goalie][1]
        else:
            goalie_pp_save[goalie] = goalie_pp[goalie]
            goalie_pp_save[goalie] = goalie_pp[goalie]

        # sh strenghts
        if goalie in goalie_sh_save.keys():
            goalie_sh_save[goalie][0] += goalie_sh[goalie][0]
            goalie_sh_save[goalie][1] += goalie_sh[goalie][1]
        else:
            goalie_sh_save[goalie] = goalie_sh[goalie]
            goalie_sh_save[goalie] = goalie_sh[goalie]


def goalie_save_percentage_calculate_all() -> None:
    for goalie in goalie_even_save.keys():

        # even strength
        if goalie_even_save[goalie][1] > 0:
            goalie_even_save[goalie] = \
                goalie_even_save[goalie][0] / goalie_even_save[goalie][1]
        else:
            goalie_even_save[goalie] = 0.0

        # pp strength
        if goalie_pp_save[goalie][1] > 0:
            goalie_pp_save[goalie] = \
                goalie_pp_save[goalie][0] / goalie_pp_save[goalie][1]
        else:
            goalie_pp_save[goalie] = 0.0

        # pk strength
        if goalie_sh_save[goalie][1] > 0:
            goalie_sh_save[goalie] = \
                goalie_sh_save[goalie][0] / goalie_sh_save[goalie][1]
        else:
            goalie_sh_save[goalie] = 0.0


def goalie_save_percentage_combine_metrics(games_played : dict={},
    pp_oppertunities : dict={}, pk_oppertunities : dict={},
    goalie_utilization : dict={}, goalie_teams_dict : dict={}) -> None:
    
    # unlike other stats which use a flat weight. Have this weight scale so that
    # roughly the percentage of time at each strength is the percent weight.
    # This is designed to be applied after some other corrections but can be
    # applied proactively as well
    for goalie in goalie_even_save.keys():

        # get roughly the total ice time for the team of this goalie
        games_played_set = games_played[goalie_teams_dict[goalie]]
        total_ice_time = games_played_set * 60

        # now calculate the percentage of time on the power play, meaning all
        # saves are short handed. Use this as short handed weight
        pp_time = pp_oppertunities[goalie_teams_dict[goalie]] * 2
        short_handed_sp_weight = pp_time / total_ice_time

        # now with less available stats in the api do a more roundabout way to
        # get the time on the penalty kill which will become the pp weight
        sh_time = pk_oppertunities[goalie_teams_dict[goalie]] * 2
        power_play_sp_weight = sh_time / total_ice_time

        # now the even strength must just be the remainder
        even_strength_sp_weight = (total_ice_time - (sh_time + pp_time)) / \
            total_ice_time
        goalie_save_percentage_rating[goalie] = (
            (goalie_even_save[goalie] * even_strength_sp_weight) + \
            (goalie_pp_save[goalie] * power_play_sp_weight) + \
            (goalie_sh_save[goalie] * short_handed_sp_weight)
        ) * goalie_utilization[goalie]
