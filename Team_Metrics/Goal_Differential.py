from .Team_Metric import Team_Metric

class Goal_Differential(Team_Metric):

    GOALS_FOR_WEIGHT = 0.45
    GOALS_AGAINST_WEIGHT = 0.55
    ENG_REDUCTION_WEIGHT = 0.3

    def __init__(self):
        super().__init__('goal_differential', 'goal_differential')

    
    def get_data_set(self, match_data : dict={}) -> dict:
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        # calculate goal differential
        home_team_goal_diff = (
            (
                (home_team_stats["goals"] -
                    (home_team_stats["empty_net_goals"] *
                    self.ENG_REDUCTION_WEIGHT)
                ) * self.GOALS_FOR_WEIGHT
            ) -
            (
                (away_team_stats["goals"] -
                    (away_team_stats["empty_net_goals"] *
                    self.ENG_REDUCTION_WEIGHT)
                ) * self.GOALS_AGAINST_WEIGHT
            )
        )
        away_team_goal_diff = (
            (
                (away_team_stats["goals"] -
                    (away_team_stats["empty_net_goals"] *
                    self.ENG_REDUCTION_WEIGHT)
                ) * self.GOALS_FOR_WEIGHT
            ) -
            (
                (home_team_stats["goals"] -
                    (home_team_stats["empty_net_goals"] *
                    self.ENG_REDUCTION_WEIGHT)
                ) * self.GOALS_AGAINST_WEIGHT
            )
        )
        return {
            home_team : home_team_goal_diff,
            away_team : away_team_goal_diff
        }
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : float=0.5) -> float:

        return super().apply_relative_scaling(relative_scalar, metric, True)

