class Utilization():    

    def __init__(self):
        self.utilization_base = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.utilization_rating = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.comparator = 'clutch'


    def get_base_dict(self, position : str="") -> dict:
        if position in self.utilization_base.keys():
            return self.utilization_base[position]
        return {}
        

    def get_dict(self, position : str="") -> dict:
        if position in self.utilization_rating.keys():
            return self.utilization_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.utilization_base.keys():
            self.utilization_base[key].clear()
        for key in self.utilization_rating.keys():
            self.utilization_rating[key].clear()


    def get_comparator(self):
        return self.comparator


    def get_data_set(self, players : dict={}) -> dict:
        utilization = {}
        for player in players.keys():

            # convert time on ice to minutes
            time_on_ice = (
                float(
                    players[player]['stats']['time_on_ice'].split(":")[0]) +
                float(
                    players[player]['stats']['time_on_ice'].split(":")[1]) / 60
            )
            utilization[player] = {
                'team' : players[player]['team'],
                "time_on_ice" : time_on_ice
            }
        return utilization


    def add_match_data(self, utilization_data : dict={},
        position : str="") -> None:

        if position not in self.utilization_base.keys():
            return {}
        for player in utilization_data.keys():
            if player in self.utilization_base[position].keys():
                self.utilization_base[position][player] += \
                    utilization_data[player]["time_on_ice"]
            else:
                self.utilization_base[position][player] = \
                    utilization_data[player]["time_on_ice"]


    def scale_by_games(self, team_games_played : dict={},
        teams_dict : dict={}, position : str="") -> None:
        if position not in self.utilization_base.keys():
            return
        for player in self.utilization_base[position].keys():
            self.utilization_rating[position][player] = (
                self.utilization_base[position][player] /
                team_games_played[teams_dict[player]]
            )
