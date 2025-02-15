class Team_Metric():

    COMPARATOR_LIST = [
        'clutch', 'shot_differential', 'goal_differential', 'penalty_kill',
        'power_play', 'recent_form', 'strength_of_schedule'
    ]

    def __init__(self, name : str="", comparator : str = ""):
        self.base_rating = {}
        self.final_rating = {}
        self.trend_rating = {}
        self.games_played = {}
        self.name = name

        if comparator not in self.COMPARATOR_LIST:
            self.comparator = 'total'
        else:
            self.comparator = comparator


    def get_base_rating_dict(self) -> dict:
        return self.base_rating
    

    def get_final_rating_dict(self) -> dict:
        return self.final_rating
    

    def get_trend_rating_dict(self) -> dict:
        return self.trend_rating
    

    def get_games_played_dict(self) -> dict:
        return self.games_played
    

    def get_comparator(self) -> int:
        return self.comparator
    

    def reset_ratings(self) -> None:
        self.base_rating.clear()
        self.final_rating.clear()
        self.trend_rating.clear()
    

    def get_relative_ranking_by_date(self, ranking_date : str="",
        team : str="") -> int:

        # first check that we got some valid date, or just return 0.5
        if ranking_date == "":
            return 0.5
        
        # if the team given is not already in the trend dict, then give them
        # an initial value and return that value
        if team not in self.trend_rating[ranking_date].keys():
            self.trend_rating[ranking_date][team] = 0.5
            return 0.5
        
        return self.trend_rating[ranking_date][team]
    

    def get_data_set(self, match_data : dict={}) -> dict:
        return {}
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}, increase : bool=True) -> float:

        if increase:
            if metric[self.name] > 0:
                metric[self.name] *= 1 + relative_scalar
            else:
                metric[self.name] /= 1 + relative_scalar    
        else:
            if metric[self.name] > 0:
                metric[self.name] /= 1 + relative_scalar
            else:
                metric[self.name] *= 1 + relative_scalar
        return metric


    def add_match_data(self, data_set : dict={}) -> None:
        for team in data_set.keys():

            # if the team is in the base rating, update
            if team in self.base_rating.keys():
                self.base_rating[team] += data_set[team][self.name]
                self.games_played[team] += 1

            # otherwise create the rating for the team
            else:
                self.base_rating[team] = data_set[team][self.name]
                self.games_played[team] = 1


    def scale_rating(self) -> None:
        for team in self.base_rating.keys():
            self.final_rating[team] = (
                self.base_rating[team] / self.games_played[team]
            )

    
    def update_trend(self, date : str="") -> None:
        if (date == "") or (date in self.trend_rating.keys()):
            return
        self.trend_rating[date] = {}
        for team in self.final_rating.keys():
            self.trend_rating[date][team] = self.final_rating[team]
