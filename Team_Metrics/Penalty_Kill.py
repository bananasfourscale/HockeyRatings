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
                'net_pk_goals_against' : float(
                    away_team_stats["power_play_goals"] -
                    home_team_stats["short_handed_goals"],
                ),
                'pk_chances' : home_team_stats["short_handed_chances"]
            },
            away_team : {
                'net_pk_goals_against' : float(
                    home_team_stats["power_play_goals"] -
                    away_team_stats["short_handed_goals"],
                ),
                'pk_chances' : away_team_stats["short_handed_chances"]
            }
        }
    
    
    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}) -> dict:

        if metric['net_pk_goals_against'] > 0:
            metric['net_pk_goals_against'] = super().apply_relative_scaling(
                relative_scalar, metric['net_pk_goals_against'], False)
        else:
            metric['net_pk_goals_against'] = super().apply_relative_scaling(
                relative_scalar, metric['net_pk_goals_against'], True)
        return metric
        

    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():
            if team in self.base_rating.keys():
                self.base_rating[team] += data_set[team]['net_pk_goals_against']
                self.pk_chances[team] += data_set[team]['pk_chances']
            else:
                self.base_rating[team] = data_set[team]['net_pk_goals_against']
                self.pk_chances[team] = data_set[team]['pk_chances']
        

    def scale_rating(self) -> None:

        # divide by sample size of pk chances rather than games played
        for team in self.base_rating.keys():
            self.final_rating[team] = (
                self.base_rating[team] / self.pk_chances[team]
            )