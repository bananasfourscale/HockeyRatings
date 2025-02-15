from .Player_Metric import Player_Metric

class Save_Percentage(Player_Metric):

    def __init__(self):
        self.goalie_even_save = {}
        self.goalie_even_save_percent = {}
        self.goalie_pp_save = {}
        self.goalie_pp_save_percent = {}
        self.goalie_sh_save = {}
        self.goalie_sh_save_percent = {}
        super().__init__('save_percentage', 'total')


    def get_dict(self) -> dict:
        return self.goalie_save_percentage_rating


    def rating_reset(self) -> None:
        self.goalie_even_save.clear()
        self.goalie_even_save_percent.clear()
        self.goalie_pp_save.clear()
        self.goalie_pp_save_percent.clear()
        self.goalie_sh_save.clear()
        self.goalie_sh_save_percent.clear()
        super().reset_ratings()


    def get_data_set(self, match_data : dict={}) -> list:
        sp_dict = {}

        # loop through and populate the time on ice
        for goalie in match_data.keys():

            # get even strength data
            even_strength_sp = {
                'saves' : match_data[goalie]['stats']["even_saves"],
                'shots' : match_data[goalie]['stats']["even_shots"]
            }

            # get powerplay data if it exist (own team short handed)
            power_play_sp = {
                'saves' : match_data[goalie]['stats']["power_play_saves"],
                'shots' : match_data[goalie]['stats']["power_play_shots"]
            }

            # get short handed data if it exist (own team power play)
            penalty_kill_sp = {
                'saves' : match_data[goalie]['stats']["short_handed_saves"],
                'shots' : match_data[goalie]['stats']["short_handed_shots"]
            }

            # add all the data to one dict for this goalie
            sp_dict[goalie] = {self.name :
                {
                    'even_save_per' : even_strength_sp,
                    'pp_save_per' : power_play_sp,
                    'pk_save_per' : penalty_kill_sp
                }
            }
        return sp_dict
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}):

        metric[self.name]['even_save_per']['saves'] *= 1 + relative_scalar
        metric[self.name]['pp_save_per']['saves'] *= 1 + relative_scalar
        metric[self.name]['pk_save_per']['saves'] *= 1 + relative_scalar
        return metric


    def add_match_data(self, goalie_save_percentage_data : dict={},
        position : str="G") -> None:


        for goalie in goalie_save_percentage_data.keys():
            goalie_even = (
                goalie_save_percentage_data[goalie][self.name][
                    'even_save_per'])
            goalie_pp = (
                goalie_save_percentage_data[goalie][self.name]['pp_save_per'])
            goalie_sh = (
                goalie_save_percentage_data[goalie][self.name]['pk_save_per'])

            # even strength
            if goalie in self.goalie_even_save.keys():
                self.goalie_even_save[goalie]['saves'] += (
                    goalie_even['saves']
                )
                self.goalie_even_save[goalie]['shots'] += (
                    goalie_even['shots']
                )
                self.games_played[goalie] += 1
            else:
                self.goalie_even_save[goalie] = {
                    'saves' : goalie_even['saves'],
                    'shots' : goalie_even['shots']
                }
                self.games_played[goalie] = 1

            # pp strengths
            if goalie in self.goalie_pp_save.keys():
                self.goalie_pp_save[goalie]['saves'] += (
                    goalie_pp['saves']
                )
                self.goalie_pp_save[goalie]['shots'] += (
                    goalie_pp['shots']
                )
            else:
                self.goalie_pp_save[goalie] = {
                    'saves' : goalie_pp['saves'],
                    'shots' : goalie_pp['shots']
                }

            # sh strenghts
            if goalie in self.goalie_sh_save.keys():
                self.goalie_sh_save[goalie]['saves'] += (
                    goalie_sh['saves']
                )
                self.goalie_sh_save[goalie]['shots'] += (
                    goalie_sh['shots']
                )
            else:
                self.goalie_sh_save[goalie] = {
                    'saves' : goalie_sh['saves'],
                    'shots' : goalie_sh['shots']
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


    def combine_metrics(self, game_time : dict={},
        pp_oppertunities : dict={}, pk_oppertunities : dict={},
        goalie_utilization : dict={}, goalie_teams_dict : dict={}) -> None:
        
        # unlike other stats which use a flat weight. Have this weight scale
        # so that roughly the percentage of time at each strength is the
        # percent weight. This is designed to be applied after some other
        # corrections but can be applied proactively as well
        for goalie in self.goalie_even_save.keys():

            # get roughly the total ice time for the team of this goalie
            total_ice_time = game_time[goalie]

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
            self.base_rating["G"][goalie] = (
                (self.goalie_even_save_percent[goalie] *
                    even_strength_sp_weight) +
                (self.goalie_pp_save_percent[goalie] * power_play_sp_weight) +
                (self.goalie_sh_save_percent[goalie] * short_handed_sp_weight)
            )

            # now update the final rating by scaling by utilization score
            self.final_rating["G"][goalie] = (
                self.base_rating["G"][goalie] * goalie_utilization[goalie]
            )


    def scale_rating(self, external_scalar_metric : dict={}):
        self.calculate_all()
        self.combine_metrics(external_scalar_metric['game_time'],
            external_scalar_metric['pp_opertunities'],
            external_scalar_metric['pk_oppertunities'],
            external_scalar_metric['utilization'],
            external_scalar_metric['goalie_teams'])
        
