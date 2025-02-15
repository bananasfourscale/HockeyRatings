from .Team_Metric import Team_Metric

class Shot_Differential(Team_Metric):

    SHOTS_FOR_WEIGHT = 0.45
    SHOTS_AGAINST_WEIGHT = 0.55

    def __init__(self):
        super().__init__('shot_differential', 'shot_differential')


    def get_data_set(self, match_data : dict={}) -> dict:
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        # calculate shot differential
        home_team_shot_diff = float(
            (home_team_stats["shots"] * self.SHOTS_FOR_WEIGHT) -
            (away_team_stats["shots"] * self.SHOTS_AGAINST_WEIGHT)
        )
        away_team_shot_diff = float(
            (away_team_stats["shots"] * self.SHOTS_FOR_WEIGHT) -
            (home_team_stats["shots"] * self.SHOTS_AGAINST_WEIGHT)
        )
        return {
            home_team : {self.name : home_team_shot_diff},
            away_team : {self.name : away_team_shot_diff}
        }
