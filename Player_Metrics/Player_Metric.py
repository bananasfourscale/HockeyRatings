class Player_Metric():

    COMPARATOR_LIST = [
        'clutch', 'shot_differential', 'goal_differential', 'penalty_kill',
        'power_play', 'recent_form', 'strength_of_schedule'
    ]

    def __init__(self, name : str="", comparator : str = ""):
        self.base_rating = {
            'D' : {},
            'C' : {},
            'G' : {},
        }
        self.final_rating = {
            'D' : {},
            'C' : {},
            'G' : {},
        }
        self.trend_rating = {
            'D' : {},
            'C' : {},
            'G' : {},
        }
        self.games_played = {}
        self.name = name

        if comparator not in self.COMPARATOR_LIST:
            self.comparator = 'total'
        else:
            self.comparator = comparator


    def get_base_rating_dict(self, position : str="") -> dict:
        if position == "":
            return {}
        return self.base_rating[position]
    

    def get_final_rating_dict(self, position : str="") -> dict:
        if position == "":
            return {}
        return self.final_rating[position]
    

    def get_trend_rating_dict(self, position) -> dict:
        if position == "":
            return {}
        return self.trend_rating[position]
    

    def get_games_played_dict(self) -> dict:
        return self.games_played
    

    def get_comparator(self) -> int:
        return self.comparator
    

    def reset_ratings(self) -> None:
        for key in self.base_rating.keys():
            self.base_rating[key].clear()
        for key in self.final_rating.keys():
            self.final_rating[key].clear()
        for key in self.trend_rating.keys():
            self.trend_rating[key].clear()
    

    def get_data_set(self, match_data : dict={}) -> dict:
        return {}
    

    def apply_relative_scaling(self, relative_scalar : float=0.5,
        metric : dict={}, increase : bool=True) -> float:

        try:
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
        except TypeError:
            print(metric)
        return metric


    def add_match_data(self, data_set : dict={}, position : str="C") -> None:
        for player in data_set.keys():

            # if the team is in the base rating, update
            if player in self.base_rating[position].keys():
                self.base_rating[position][player] += (
                    data_set[player][self.name])
                self.games_played[player] += 1

            # otherwise create the rating for the team
            else:
                self.base_rating[position][player] = data_set[player][self.name]
                self.games_played[player] = 1


    def scale_rating(self, position : str="C",
        external_scalar_metric : dict={}) -> None:

        for player in self.base_rating[position].keys():
            self.final_rating[position][player] = (
                self.base_rating[position][player] *
                (1 + external_scalar_metric[player])
            )

    
    def update_trend(self, date : str="") -> None:
        if (date == "") or (date in self.trend_rating.keys()):
            return
        self.trend_rating[date] = {}
        for position in self.final_rating.keys():
            for player in self.final_rating[position].keys():
                self.trend_rating[date][position][player] = (
                    self.final_rating[position][player]
                )


    def get_uncorrected_print_args(self, prefix : str="",
        position : str="C") -> list:

        if position == "C":
            title_group = "Forward"
        elif position == "D":
            title_group = "Defensemen"
        else:
            title_group = "Goalies"
        data_file_name = "{}_{}_{}_base.csv".format(prefix, title_group,
            self.name)
        arg_dict = {
            "data_file_name" :
                "Output_Files/Player_Files/Instance_Files/" + data_file_name,
            "title_args" : [title_group, self.name + "Base", "Team"],
            "data_dict" : self.final_rating[position],
            "graph_name" :
                "Graphs/{}/{}/{}_base.png".format(title_group,
                    self.name, prefix + self.name),
            "ascending_order" : False,
        }
        return [arg_dict]
    

    def get_corrected_print_args(self, prefix : str="",
        position : str="C") -> list:

        if position == "C":
            title_group = "Forward"
        elif position == "D":
            title_group = "Defensemen"
        else:
            title_group = "Goalies"
        data_file_name = "{}_{}_{}_corrected.csv".format(prefix, title_group,
            self.name)
        arg_dict = {
            "data_file_name" :
                "Output_Files/Player_Files/Instance_Files/" + data_file_name,
            "title_args" : [title_group, self.name + "Corrected", "Team"],
            "data_dict" : self.final_rating[position],
            "graph_name" :
                "Graphs/{}/{}/{}_corrected.png".format(title_group,
                    self.name, prefix + self.name),
            "ascending_order" : False,
        }
        return [arg_dict]
