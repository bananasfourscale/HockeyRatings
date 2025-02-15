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
                self.name : float(
                    home_team_stats["power_play_goals"] -
                    away_team_stats["short_handed_goals"],
                ),
                'pp_chances' : home_team_stats["power_play_chances"]
            },
            away_team : {
                self.name : float(
                    away_team_stats["power_play_goals"] -
                    home_team_stats["short_handed_goals"],
                ),
                'pp_chances' : away_team_stats["power_play_chances"]
            }
        }


    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():
            if team in self.base_rating.keys():
                self.base_rating[team] += data_set[team][self.name]
                self.pp_chances[team] += data_set[team]['pp_chances']
            else:
                self.base_rating[team] = data_set[team][self.name]
                self.pp_chances[team] = data_set[team]['pp_chances']


    def scale_rating(self) -> None:

        # divide by sample size of pp chances rather than games played
        for team in self.base_rating.keys():
            self.final_rating[team] = (
                self.base_rating[team] / self.pp_chances[team]
            )
