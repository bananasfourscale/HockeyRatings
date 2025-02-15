from .Team_Metric import Team_Metric

class Strength_of_Schedule(Team_Metric):

    # weights
    WIN_REGULATION_WEIGHT = 1.0
    LOSE_REGULATION_WEIGHT = 0.0
    WIN_OT_WEIGHT = 0.33
    LOSE_OT_WEIGHT = 0.10
    WIN_SO_WEIGHT = 0.10
    LOSE_SO_WEIGHT = 0.05

    # match indecies
    AWAY_TEAM = 0
    AWAY_SCORE = 1
    HOME_TEAM = 2
    HOME_SCORE = 3
    EXTRA_TIME = 4

    def __init__(self):
        super().__init__('strength_of_schedule', 'total')


    def get_data_set(self, match_data : dict={}) -> dict:
        game_value = {}
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]
        home_score_final = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"] +
            home_team_stats["third_period_goals"] +
            home_team_stats["OT_goals"] +
            home_team_stats["SO_goals"]
        )
        away_score_final = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"] +
            away_team_stats["third_period_goals"] +
            away_team_stats["OT_goals"] +
            away_team_stats["SO_goals"]
        )
        final_game_state = match_data['game_stats']['result']

        # determine who won and lost the game
        if home_score_final > away_score_final:
            winner = home_team
            loser = away_team
        else:
            winner = away_team
            loser = home_team

        # now give points between 0 and 1 to each team
        # depending on the game result
        if final_game_state == "REG":
            game_value[winner] = \
                self.WIN_REGULATION_WEIGHT
            game_value[loser] = \
                self.LOSE_REGULATION_WEIGHT
        elif final_game_state == "OT":
            game_value[winner] = (
                self.WIN_OT_WEIGHT
            )
            game_value[loser] = (
                self.LOSE_OT_WEIGHT
            )
        else:
            game_value[winner] = (
                self.WIN_SO_WEIGHT
            )
            game_value[loser] = (
                self.LOSE_SO_WEIGHT
            )
        return {
            winner : {self.name : game_value[winner]},
            loser : {self.name : game_value[loser]}
        }
