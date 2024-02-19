goalie_even_save = {}

goalie_even_save_percent = {}

goalie_pp_save = {}

goalie_pp_save_percent = {}

goalie_sh_save = {}

goalie_sh_save_percent = {}

goalie_save_percentage_rating = {}


def goalie_save_percentage_get_dict() -> dict:
    return goalie_save_percentage_rating


def goalie_save_percentage_reset() -> None:
    goalie_even_save.clear()
    goalie_even_save_percent.clear()
    goalie_pp_save.clear()
    goalie_pp_save_percent.clear()
    goalie_sh_save.clear()
    goalie_sh_save_percent.clear()
    goalie_save_percentage_rating.clear()


def goalie_save_percentage_get_data_set(match_data : dict={}) -> list:
    even_strength_sp = {}
    power_play_sp = {}
    penalty_kill_sp = {}

    # loop through and populate the time on ice
    for goalie in match_data.keys():

        # get even strength data
        # try:
        even_strength_sp[goalie] = {
            'saves' : match_data[goalie]['stats']["even_saves"],
            'shots' : match_data[goalie]['stats']["even_shots"]
        }
        # except KeyError:
        #     even_strength_sp[goalie] = [match_data[goalie][1]["saves"]**2,
        #         match_data[goalie][1]["shots"]]

        # get powerplay data if it exist (own team short handed)
        # try:
        power_play_sp[goalie] = {
            'saves' : match_data[goalie]['stats']["power_play_saves"],
            'shots' : match_data[goalie]['stats']["power_play_shots"]
        }
        # except KeyError:
        #     power_play_sp[goalie] = [match_data[goalie][1]["saves"]**2,
        #         match_data[goalie][1]["shots"]]

        # get short handed data if it exist (own team power play)
        # try:
        penalty_kill_sp[goalie] = {
            'saves' : match_data[goalie]['stats']["short_handed_saves"],
            'shots' : match_data[goalie]['stats']["short_handed_shots"]
        }
        # except KeyError:
        #     penalty_kill_sp[goalie] = [match_data[goalie][1]["saves"]**2,
        #         match_data[goalie][1]["shots"]]
    return {
        'even_save_per' : even_strength_sp,
        'pp_save_per' : power_play_sp,
        'pk_save_per' : penalty_kill_sp
    }


def goalie_save_percentage_add_match_data(goalie_save_percentage_data : dict={})\
                                                                        -> None:
    goalie_even = goalie_save_percentage_data['even_save_per']
    goalie_pp = goalie_save_percentage_data['pp_save_per']
    goalie_sh = goalie_save_percentage_data['pk_save_per']
    for goalie in goalie_save_percentage_data['even_save_per'].keys():

        # even strength
        if goalie in goalie_even_save.keys():
            goalie_even_save[goalie]['saves'] += goalie_even[goalie]['saves']
            goalie_even_save[goalie]['shots'] += goalie_even[goalie]['shots']
        else:
            goalie_even_save[goalie]['saves'] = goalie_even[goalie]['saves']
            goalie_even_save[goalie]['shots'] = goalie_even[goalie]['shots']

        # pp strengths
        if goalie in goalie_pp_save.keys():
            goalie_pp_save[goalie]['saves'] += goalie_pp[goalie]['saves']
            goalie_pp_save[goalie]['shots'] += goalie_pp[goalie]['shots']
        else:
            goalie_pp_save[goalie]['saves'] = goalie_pp[goalie]['saves']
            goalie_pp_save[goalie]['shots'] = goalie_pp[goalie]['shots']

        # sh strenghts
        if goalie in goalie_sh_save.keys():
            goalie_sh_save[goalie]['saves'] += goalie_sh[goalie]['saves']
            goalie_sh_save[goalie]['shots'] += goalie_sh[goalie]['shots']
        else:
            goalie_sh_save[goalie]['saves'] = goalie_sh[goalie]['saves']
            goalie_sh_save[goalie]['shots'] = goalie_sh[goalie]['shots']


def goalie_save_percentage_calculate_all() -> None:
    for goalie in goalie_even_save.keys():

        # even strength
        if goalie_even_save[goalie]['shots'] > 0:
            goalie_even_save_percent[goalie] = (
                goalie_even_save[goalie]['saves'] /
                goalie_even_save[goalie]['shots']
            )
        else:
            goalie_even_save_percent[goalie] = 0.0

        # pp strength
        if goalie_pp_save[goalie]['shots'] > 0:
            goalie_pp_save_percent[goalie] = (
                goalie_pp_save[goalie]['saves'] /
                goalie_pp_save[goalie]['shots']
            )
        else:
            goalie_pp_save_percent[goalie] = 0.0

        # pk strength
        if goalie_sh_save[goalie]['shots'] > 0:
            goalie_sh_save_percent[goalie] = (
                goalie_sh_save[goalie]['saves'] /
                goalie_sh_save[goalie]['shots']
            )
        else:
            goalie_sh_save_percent[goalie] = 0.0


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
        even_strength_sp_weight = (
            (total_ice_time - (sh_time + pp_time)) / total_ice_time
        )
        goalie_save_percentage_rating[goalie] = (
            (goalie_even_save_percent[goalie] * even_strength_sp_weight) +
            (goalie_pp_save_percent[goalie] * power_play_sp_weight) +
            (goalie_sh_save_percent[goalie] * short_handed_sp_weight)
        ) * goalie_utilization[goalie]
