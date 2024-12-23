class PlusMinus():

    def __init__(self):
        self.plus_minus_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.plus_minus_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }


    def get_base_dict(self, position : str="") -> dict:
        if position in self.plus_minus_base.keys():
            return self.plus_minus_base[position]
        return {}
        

    def get_dict(self, position : str="") -> dict:
        if position in self.plus_minus_rating.keys():
            return self.plus_minus_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.plus_minus_base.keys():
            self.plus_minus_base[key].clear()
        for key in self.plus_minus_rating.keys():
            self.plus_minus_rating[key].clear()


    def get_data_set(self, players : dict={}) -> dict:
        plus_minus = {}
        for player in players.keys():

            # convert time on ice to minutes
            plus_minus[player] = {
                "plus_minus" : players[player]['stats']['plus_minus']
            }
        return plus_minus


    def add_match_data(self, plus_minus_data : dict={},
        position : str="") -> None:

        if position not in self.plus_minus_base.keys():
            return {}
        for player in plus_minus_data.keys():
            if player in self.plus_minus_base[position].keys():
                self.plus_minus_base[position][player] += (
                    plus_minus_data[player]["plus_minus"]
                )
            else:
                self.plus_minus_base[position][player] = (
                    plus_minus_data[player]["plus_minus"]
                )
                

    def scale_by_utilization(self, utilization : dict={},
        position : str="") -> None:

        if position not in self.plus_minus_base.keys():
            return
        for player in self.plus_minus_base[position].keys():
            self.plus_minus_rating[position][player] = (
                self.plus_minus_base[position][player] * utilization[player]
            )
