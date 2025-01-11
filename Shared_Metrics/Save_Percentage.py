class Save_Percentage():

    def __init__(self):
        self.goalie_even_save = {}
        self.goalie_even_save_percent = {}
        self.goalie_pp_save = {}
        self.goalie_pp_save_percent = {}
        self.goalie_sh_save = {}
        self.goalie_sh_save_percent = {}
        self.goalie_save_percentage_rating = {}
        self.comparator = 'total'


    def get_dict(self) -> dict:
        return self.goalie_save_percentage_rating


    def rating_reset(self) -> None:
        self.goalie_even_save.clear()
        self.goalie_even_save_percent.clear()
        self.goalie_pp_save.clear()
        self.goalie_pp_save_percent.clear()
        self.goalie_sh_save.clear()
        self.goalie_sh_save_percent.clear()
        self.goalie_save_percentage_rating.clear()


    def get_comparator(self):
        return self.comparator


    def get_data_set(self, match_data : dict={}) -> list:
        even_strength_sp = {}
        power_play_sp = {}
        penalty_kill_sp = {}

        # loop through and populate the time on ice
        for goalie in match_data.keys():

            # get even strength data
            even_strength_sp[goalie] = {
                'saves' : match_data[goalie]['stats']["even_saves"],
                'shots' : match_data[goalie]['stats']["even_shots"]
            }

            # get powerplay data if it exist (own team short handed)
            power_play_sp[goalie] = {
                'saves' : match_data[goalie]['stats']["power_play_saves"],
                'shots' : match_data[goalie]['stats']["power_play_shots"]
            }

            # get short handed data if it exist (own team power play)
            penalty_kill_sp[goalie] = {
                'saves' : match_data[goalie]['stats']["short_handed_saves"],
                'shots' : match_data[goalie]['stats']["short_handed_shots"]
            }
        return {
            'even_save_per' : even_strength_sp,
            'pp_save_per' : power_play_sp,
            'pk_save_per' : penalty_kill_sp
        }


    def add_match_data(self, goalie_save_percentage_data : dict={}) -> None:
        goalie_even = goalie_save_percentage_data['even_save_per']
        goalie_pp = goalie_save_percentage_data['pp_save_per']
        goalie_sh = goalie_save_percentage_data['pk_save_per']
        for goalie in goalie_save_percentage_data['even_save_per'].keys():

            # even strength
            if goalie in self.goalie_even_save.keys():
                self.goalie_even_save[goalie]['saves'] += (
                    goalie_even[goalie]['saves']
                )
                self.goalie_even_save[goalie]['shots'] += (
                    goalie_even[goalie]['shots']
                )
            else:
                self.goalie_even_save[goalie] = {
                    'saves' : goalie_even[goalie]['saves'],
                    'shots' : goalie_even[goalie]['shots']
                }

            # pp strengths
            if goalie in self.goalie_pp_save.keys():
                self.goalie_pp_save[goalie]['saves'] += (
                    goalie_pp[goalie]['saves']
                )
                self.goalie_pp_save[goalie]['shots'] += (
                    goalie_pp[goalie]['shots']
                )
            else:
                self.goalie_pp_save[goalie] = {
                    'saves' : goalie_pp[goalie]['saves'],
                    'shots' : goalie_pp[goalie]['shots']
                }

            # sh strenghts
            if goalie in self.goalie_sh_save.keys():
                self.goalie_sh_save[goalie]['saves'] += (
                    goalie_sh[goalie]['saves']
                )
                self.goalie_sh_save[goalie]['shots'] += (
                    goalie_sh[goalie]['shots']
                )
            else:
                self.goalie_sh_save[goalie] = {
                    'saves' : goalie_sh[goalie]['saves'],
                    'shots' : goalie_sh[goalie]['shots']
                }


    def calculate_all(self) -> None:
        for goalie in self.goalie_even_save.keys():

            # even strength
            if self.goalie_even_save[goalie]['shots'] > 0:
                self.goalie_even_save_percent[goalie] = (
                    self.goalie_even_save[goalie]['saves'] /
                    self.goalie_even_save[goalie]['shots']
                )
            else:
                self.goalie_even_save_percent[goalie] = 0.0

            # pp strength
            if self.goalie_pp_save[goalie]['shots'] > 0:
                self.goalie_pp_save_percent[goalie] = (
                    self.goalie_pp_save[goalie]['saves'] /
                    self.goalie_pp_save[goalie]['shots']
                )
            else:
                self.goalie_pp_save_percent[goalie] = 0.0

            # pk strength
            if self.goalie_sh_save[goalie]['shots'] > 0:
                self.goalie_sh_save_percent[goalie] = (
                    self.goalie_sh_save[goalie]['saves'] /
                    self.goalie_sh_save[goalie]['shots']
                )
            else:
                self.goalie_sh_save_percent[goalie] = 0.0


    def combine_metrics(self, games_played : dict={},
        pp_oppertunities : dict={}, pk_oppertunities : dict={},
        goalie_utilization : dict={}, goalie_teams_dict : dict={}) -> None:
        
        # unlike other stats which use a flat weight. Have this weight scale
        # so that roughly the percentage of time at each strength is the
        # percent weight. This is designed to be applied after some other
        # corrections but can be applied proactively as well
        for goalie in self.goalie_even_save.keys():

            # get roughly the total ice time for the team of this goalie
            games_played_set = games_played[goalie_teams_dict[goalie]]
            total_ice_time = games_played_set * 60

            # now calculate the percentage of time on the power play,
            # meaning all saves are short handed.
            # Use this as short handed weight
            pp_time = pp_oppertunities[goalie_teams_dict[goalie]] * 2
            short_handed_sp_weight = pp_time / total_ice_time

            # now with less available stats in the api do a more
            # roundabout way to get the time on the penalty kill which 
            # will become the pp weight
            sh_time = pk_oppertunities[goalie_teams_dict[goalie]] * 2
            power_play_sp_weight = sh_time / total_ice_time

            # now the even strength must just be the remainder
            even_strength_sp_weight = (
                (total_ice_time - (sh_time + pp_time)) / total_ice_time
            )
            self.goalie_save_percentage_rating[goalie] = (
                (self.goalie_even_save_percent[goalie] *
                    even_strength_sp_weight) +
                (self.goalie_pp_save_percent[goalie] * power_play_sp_weight) +
                (self.goalie_sh_save_percent[goalie] * short_handed_sp_weight)
            ) * goalie_utilization[goalie]
