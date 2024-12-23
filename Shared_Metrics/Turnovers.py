class Turnovers():

    def __init__(self):
        self.turnovers_base = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.turnovers_rating = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }


    def get_base_dict(self, position : str="") -> dict:
        if position in self.turnovers_base.keys():
            return self.turnovers_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.turnovers_rating.keys():
            return self.turnovers_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.turnovers_base.keys():
            self.turnovers_base[key].clear()
        for key in self.turnovers_rating.keys():
            self.turnovers_rating[key].clear()


    def get_data_set(self, players : dict={}) -> dict:
        turnovers = {}
        for player in players.keys():
            turnovers[player] = {
                'turnovers' : (
                    players[player]['stats']['takeaways'] -
                    players[player]['stats']['giveaways']
                )
            }
        return turnovers


    def add_match_data(self, turnovers_data : dict = {},
        position : str="") -> None:

        if position not in self.turnovers_base.keys():
            return {}
        for player in turnovers_data.keys():
            if player in self.turnovers_base[position].keys():
                self.turnovers_base[position][player] += (
                    turnovers_data[player]["turnovers"]
                )
            else:
                self.turnovers_base[position][player] = (
                    turnovers_data[player]["turnovers"]
                )
                    

    def scale_by_utilization(self, utilization : dict={},
        position : str="") -> None:

        if position not in self.turnovers_base.keys():
            return
        for player in self.turnovers_base[position].keys():
            self.turnovers_rating[position][player] = (
                self.turnovers_base[position][player] * utilization[player]
            )
