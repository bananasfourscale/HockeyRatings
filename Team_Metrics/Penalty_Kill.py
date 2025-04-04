from .Team_Metric import Team_Metric

class Penalty_Kill(Team_Metric):

    def __init__(self):
        super().__init__('penalty_kill', 'power_play')
        self.pk_chances = {}

    
    def get_pk_chances_dict(self) -> dict:
        return self.pk_chances
    

    def get_data_set(self,  match_data : dict={}) -> dict:

        # get home and away team
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        return {
            home_team : {
                self.name : float(
                    away_team_stats["power_play_goals"] -
                    home_team_stats["short_handed_goals"],
                ),
                'pk_chances' : home_team_stats["short_handed_chances"]
            },
            away_team : {
                self.name : float(
                    home_team_stats["power_play_goals"] -
                    away_team_stats["short_handed_goals"],
                ),
                'pk_chances' : away_team_stats["short_handed_chances"]
            }
        }
    
    
    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}) -> dict:

        return super().apply_relative_scaling(relative_scalar, metric, False)
        

    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():
            if team in self.base_rating.keys():
                self.base_rating[team] += data_set[team][self.name]
                self.pk_chances[team] += data_set[team]['pk_chances']
            else:
                self.base_rating[team] = data_set[team][self.name]
                self.pk_chances[team] = data_set[team]['pk_chances']
        

    def scale_rating(self) -> None:

        # divide by sample size of pk chances rather than games played
        for team in self.base_rating.keys():
            self.final_rating[team] = (
                self.base_rating[team] / self.pk_chances[team]
            )

    
    def get_uncorrected_print_args(self, prefix : str="") -> list:
        data_file_name = "{}_{}_base.csv".format(prefix, self.name)
        arg_dict = {
            "data_file_name" :
                "Output_Files/Team_Files/Instance_Files/" + data_file_name,
            "title_args" : ["Team", self.name + "Base"],
            "data_dict" : self.final_rating,
            "graph_name" : 
                "Graphs/Teams/{}/{}_base.png".format(self.name,
                    prefix + self.name),
            "ascending_order" : True,
        }
        return [arg_dict]
    

    def get_correction_arg_list(self) -> list:
        arg_dict = {
            "component_score" : self.get_final_rating_dict(),
            "asccending" : True
        }
        return [arg_dict]