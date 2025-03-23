from .Player_Metric import Player_Metric

class Goals_Against(Player_Metric):

    def __init__(self):
        super().__init__('goals_against', 'total')


    def get_data_set(self, match_data : dict={}) -> dict:
        goals_against = {}
        for goalie in match_data.keys():
            shot_total = (
                match_data[goalie]['stats']["even_shots"] + 
                match_data[goalie]['stats']["power_play_shots"] + 
                match_data[goalie]['stats']["short_handed_shots"]
            )
            save_total = (
                match_data[goalie]['stats']["even_saves"] + 
                match_data[goalie]['stats']["power_play_saves"] + 
                match_data[goalie]['stats']["short_handed_saves"]
            )
            goals_against[goalie] = {self.name : shot_total - save_total}
        return goals_against
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}):

        return super().apply_relative_scaling(relative_scalar, metric, False)
    

    def get_correction_arg_list(self, position : str="C") -> list:
        arg_dict = {
            "component_score" : self.get_final_rating_dict(position),
            "asccending" : True
        }
        return [arg_dict]
