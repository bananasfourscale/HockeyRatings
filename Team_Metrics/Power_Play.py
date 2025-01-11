from .Team_Metric import Team_Metric

class Power_Play(Team_Metric):

    def __init__(self):
        super().__init__('power_play', 'penalty_kill')
        self.pp_chances = {}

    
    def get_pp_chances_dict(self) -> dict:
        return self.pp_chances
    

    def get_data_set(self,  match_data : dict={}):

        # get home and away team
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        return {
            home_team : {
                'net_pp_goals_for' : float(
                    home_team_stats["power_play_goals"] -
                    away_team_stats["short_handed_goals"],
                ),
                'pp_chances' : home_team_stats["power_play_chances"]
            },
            away_team : {
                'net_pp_goals_for' : float(
                    away_team_stats["power_play_goals"] -
                    home_team_stats["short_handed_goals"],
                ),
                'pp_chances' : away_team_stats["power_play_chances"]
            }
        }
    
    
    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}) -> dict:

        if metric['net_pp_goals_for'] > 0:
            metric['net_pp_goals_for'] = super().apply_relative_scaling(
                relative_scalar, metric['net_pp_goals_for'], True)
        else:
            metric['net_pp_goals_for'] = super().apply_relative_scaling(
                relative_scalar, metric['net_pp_goals_for'], False)
        return metric
        

    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():
            if team in self.base_rating.keys():
                self.base_rating[team] += data_set[team]['net_pp_goals_for']
                self.pp_chances[team] += data_set[team]['pp_chances']
            else:
                self.base_rating[team] = data_set[team]['net_pp_goals_for']
                self.pp_chances[team] = data_set[team]['pp_chances']
        

    def scale_rating(self) -> None:

        # divide by sample size of pp chances rather than games played
        for team in self.base_rating.keys():
            self.final_rating[team] = (
                self.base_rating[team] / self.pp_chances[team]
            )