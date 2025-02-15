from math import pow, log
from .Team_Metric import Team_Metric

class Clutch(Team_Metric):

    LOG_FACTOR = 2
    POW_FACTOR = 1.5
    SECOND_FACTOR = 1.25
    THIRD_FACTOR = 1.5

    def __init__(self):
        super().__init__('clutch', 'total')


    def get_data_set(self, match_data : dict={}) -> dict:

        # home team data
        home_points = 0.0
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        # print(home_team_stats)
        home_score_first = home_team_stats["first_period_goals"]
        home_score_second = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"]
        )
        home_score_third = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"] +
            home_team_stats["third_period_goals"]
        )
        home_score_OT = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"] +
            home_team_stats["third_period_goals"] + home_team_stats["OT_goals"]
        )
        home_score_final = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"] +
            home_team_stats["third_period_goals"] +
            home_team_stats["OT_goals"] +
            home_team_stats["SO_goals"]
        )

        # away team data
        away_points = 0.0
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]
        away_score_first = away_team_stats["first_period_goals"]
        away_score_second = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"]
        )
        away_score_third = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"] +
            away_team_stats["third_period_goals"]
        )
        away_score_OT = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"] +
            away_team_stats["third_period_goals"] + away_team_stats["OT_goals"]
        )
        away_score_final = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"] +
            away_team_stats["third_period_goals"] +
            away_team_stats["OT_goals"] +
            away_team_stats["SO_goals"]
        )

        # get diff from each period
        first_diff = abs(away_score_first - home_score_first)
        second_diff = abs(away_score_second - home_score_second)
        third_diff = abs(away_score_third - home_score_third)

        # if the away team won
        if away_score_final > home_score_final:

            # first period points
            if away_score_first < home_score_first:
                away_points += log(first_diff, self.LOG_FACTOR)
                home_points -= pow(first_diff, self.POW_FACTOR)
            elif away_score_first > home_score_first:
                away_points += log(first_diff, self.LOG_FACTOR)
            else:
                away_points += 0.5
                home_points += 0.5

            # second period points
            if away_score_second < home_score_second:
                away_points += log(second_diff * self.SECOND_FACTOR,
                    self.LOG_FACTOR)
                home_points -= pow(second_diff * self.SECOND_FACTOR,
                    self.POW_FACTOR)
            elif away_score_second > home_score_second:
                away_points += log(second_diff * self.SECOND_FACTOR,
                    self.LOG_FACTOR)
            else:
                away_points += 1
                home_points += 1

            # third period points. If not equal at this point away team has won
            # in regulation
            if away_score_third != home_score_third:
                away_points += log(third_diff * self.THIRD_FACTOR,
                    self.LOG_FACTOR)

            # if OT scores are equal we went to shootout so give both teams very
            # few points for getting this far.
            elif away_score_OT == home_score_OT:
                away_points += 0.1
                home_points += 0.1

            # otherwise the game ended in OT so give more than SO but not much
            else:
                away_points += 0.3
                home_points += 0.3

        # if the home team won
        else:

            # first period points
            if home_score_first < away_score_first:
                home_points += log(first_diff, self.LOG_FACTOR)
                away_points -= pow(first_diff, self.POW_FACTOR)
            elif home_score_first > away_score_first:
                home_points += log(first_diff, self.LOG_FACTOR)
            else:
                home_points += 0.5
                away_points += 0.5

            # second period points
            if home_score_second < away_score_second:
                home_points += log(second_diff * self.SECOND_FACTOR,
                    self.LOG_FACTOR)
                away_points -= pow(second_diff * self.SECOND_FACTOR,
                    self.POW_FACTOR)
            elif home_score_second > away_score_second:
                home_points += log(second_diff * self.SECOND_FACTOR,
                    self.LOG_FACTOR)
            else:
                home_points += 1
                away_points += 1

            # third period points. If not equal at this point away team has won
            if home_score_third != away_score_third:
                home_points += log(third_diff * self.THIRD_FACTOR,
                    self.LOG_FACTOR)

            # if OT scores are equal we went to shootout so give both teams very
            # few points for getting this far.
            elif home_score_OT == away_score_OT:
                home_points += 0.1
                away_points += 0.1

            # otherwise the game ended in OT so give more than SO but not much
            else:
                home_points += 0.3
                away_points += 0.3

        # collect all the different permutations into one data set and return
        return {
            home_team : {self.name : home_points},
            away_team : {self.name : away_points}
        }
