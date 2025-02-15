from .Team_Metric import Team_Metric

class Recent_Form(Team_Metric):

    # Class constants
    LAST_10 = 0.35
    LAST_20 = 0.25
    LAST_40 = 0.15
    TOTAL_STREAK = 0.15
    LONGEST_STREAK = 0.10


    def __init__(self):
        super().__init__('recent_form', 'recent_form')

        self.streak_info = {}
        self.total_streak_rating = {}
        self.longest_streak_rating = {}
        self.last_10_info = {}
        self.last_10_rating = {}
        self.last_20_info = {}
        self.last_20_rating = {}
        self.last_40_info = {}
        self.last_40_rating = {}
        self.comparator = 'total'


    def get_streak_dict(self) -> dict:
        return self.total_streak_rating


    def get_longest_streak_dict(self) -> dict:
        return self.longest_streak_rating


    def get_last_10_dict(self) -> dict:
        return self.last_10_rating


    def get_last_20_dict(self) -> dict:
        return self.last_20_rating


    def get_last_40_dict(self) -> dict:
        return self.last_40_rating


    def rating_reset(self) -> None:
        self.streak_info.clear()
        self.total_streak_rating.clear()
        self.last_10_info.clear()
        self.last_10_rating.clear()
        self.last_20_info.clear()
        self.last_20_rating.clear()
        self.last_40_info.clear()
        self.last_40_rating.clear()
        self.final_rating.clear()
        self.trend_rating.clear()


    def get_comparator(self):
        return self.comparator


    def get_data_set(self, match_data : dict={}) -> list:
        game_result = {}
        game_value = {}

        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]
        home_score_final = home_team_stats["first_period_goals"] + \
            home_team_stats["second_period_goals"] + \
            home_team_stats["third_period_goals"]
        away_score_final = away_team_stats["first_period_goals"] + \
            away_team_stats["second_period_goals"] + \
            away_team_stats["third_period_goals"]
        final_game_state = match_data['game_stats']['result']

        # determine the winner and loser from game score
        if home_score_final > away_score_final:
            winner = home_team
            loser = away_team
        else:
            winner = away_team
            loser = home_team

        # assign points
        game_result[winner] = "W"
        game_value[winner] = 1.0
        if final_game_state == "REG":
            game_result[loser] = "L"
            game_value[loser] = -1.0
        elif final_game_state == "OT":
            game_result[loser] = "OT"
            game_value[loser] = (-1.0 / 3.0)
        else:
            game_result[loser] = "SO"
            game_value[loser] = (-1.0 / 10.0)

        return {
            winner : {
                'game_result' : game_result[winner],
                'game_value' : game_value[winner]
            },
            loser : {
                'game_result' : game_result[loser],
                'game_value' : game_value[loser]
            }
        }
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}) -> dict:

        if metric['game_value'] > 0:
            metric['game_value'] *= 1 + relative_scalar 
        else:
            metric['game_value'] /= 1 + relative_scalar
        return metric


    def add_match_to_streak(self, streak : str="", team : str="") -> None:

        # if the team already is in the list of team streaks
        if team in self.streak_info.keys():

            # if the streak is changed, update the number of different streaks
            # in the season, and reset the current streak count
            if (streak !=
                self.streak_info[team]["current_streak_ordinal"]):

                self.streak_info[team]["current_streak_count"] = 1
                self.streak_info[team]["current_streak_ordinal"] = (streak)
                self.streak_info[team]["number_streaks"] += 1

            # if the streak continues, update the count for it and check against
            # the teams longest streak
            else:
                self.streak_info[team]["current_streak_count"] += 1
                if (self.streak_info[team]["current_streak_count"] > 
                    self.streak_info[team]["longest_streak_count"]):

                    self.streak_info[team]["longest_streak_count"] = (
                        self.streak_info[team]["current_streak_count"]
                    )
                    self.streak_info[team]["longest_streak_ordinal"] = (streak)

            # now determine how to adjust the total streak score based on the
            # result type
            if streak == "W":
                self.streak_info[team]["total_streak_score"] += 1
            if streak == "L":
                self.streak_info[team]["total_streak_score"] -= 1
            else:
                self.streak_info[team]["total_streak_score"] += (-1.0 / 3.0)

        # otherwise if we have to add the team to the streak list
        else:
            if streak == "W":
                streak_score = 1
            if streak == "L":
                streak_score = -1
            else:
                streak_score = (-1.0 / 3.0)
            self.streak_info[team] = {
                "current_streak_ordinal" : streak,
                "current_streak_count" : 1,
                "longest_streak_ordinal" : streak,
                "longest_streak_count" : 1,
                "total_streak_score" : streak_score,
                "number_streaks" : 1,
            }


    def add_match_to_recent_lists(self, match_score : float=0.0, team : str="") \
                                                                        -> None:

        # if the last ten list is already full pop the first item off
        if team in self.last_10_info.keys():
            if len(self.last_10_info[team]) >= 10:
                self.last_10_info[team].pop(0)    
            self.last_10_info[team].append(match_score)
        else:
            self.last_10_info[team] = [match_score]

        # do the same but for the last twenty list
        # if the last ten list is already full pop the first item off
        if team in self.last_20_info.keys():
            if len(self.last_20_info[team]) >= 20:
                self.last_20_info[team].pop(0)    
            self.last_20_info[team].append(match_score)
        else:
            self.last_20_info[team] = [match_score]

        # now finally do the same for last fourty
        if team in self.last_40_info.keys():
            if len(self.last_40_info[team]) >= 40:
                self.last_40_info[team].pop(0)    
            self.last_40_info[team].append(match_score)
        else:
            self.last_40_info[team] = [match_score]


    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():
            self.add_match_to_streak(data_set[team]['game_result'], team)
            self.add_match_to_recent_lists(data_set[team]['game_value'], team)


    def scale_rating(self) -> None:
        for team in self.streak_info.keys():

            # average streak score
            self.total_streak_rating[team] = (
                self.streak_info[team]["total_streak_score"] /
                self.streak_info[team]["number_streaks"]
            )

            # longest streak score
            if self.streak_info[team]['longest_streak_ordinal'] == "W":
                self.longest_streak_rating[team] = (
                    self.streak_info[team]['longest_streak_count']
                )
            elif self.streak_info[team]['longest_streak_ordinal'] == "L":
                self.longest_streak_rating[team] = (
                    self.streak_info[team]['longest_streak_count'] * -1
                )
            else:
                self.longest_streak_rating[team] = (
                    self.streak_info[team]['longest_streak_count'] *
                    (-1.0 / 3.0)
                )

            # recent games scoring
            self.last_10_rating[team] = sum(self.last_10_info[team])
            self.last_20_rating[team] = sum(self.last_20_info[team])
            self.last_40_rating[team] = sum(self.last_40_info[team])

            # combine and weight all
            self.final_rating[team] = (
                (self.total_streak_rating[team] *
                    self.TOTAL_STREAK) +
                (self.longest_streak_rating[team] *
                    self.LONGEST_STREAK) +
                (self.last_10_rating[team] *
                    self.LAST_10) +
                (self.last_20_rating[team] *
                    self.LAST_20) +
                (self.last_40_rating[team] *
                    self.LAST_40)
            )
