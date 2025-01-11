class Hitting():

    def __init__(self):
        self.hitting_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.hitting_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.comparator = 'total'


    def get_base_dict(self, position : str="") -> dict:
        if position in self.hitting_base.keys():
            return self.hitting_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.hitting_rating.keys():
            return self.hitting_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.hitting_base.keys():
            self.hitting_base[key].clear()
        for key in self.hitting_rating.keys():
            self.hitting_rating[key].clear()


    def get_comparator(self):
        return self.comparator


    def get_data_set(self, players : dict={}) -> dict:
        hitting = {}
        for player in players.keys():
            hitting[player] = {
                'hitting' : players[player]['stats']['hits'] -
                    (players[player]['stats']['hits_taken'] * 0.25)
            }
        return hitting


    def add_match_data(self, hitting_data : dict={},
        position : str="") -> None:

        if position not in self.hitting_base.keys():
            return {}
        for player in hitting_data.keys():
            if player in self.hitting_base[position].keys():
                self.hitting_base[position][player] += (
                    hitting_data[player]["hitting"]
                )
            else:
                self.hitting_base[position][player] = (
                    hitting_data[player]["hitting"]
                )
                    

    def scale_by_games(self, team_games_played : dict={},
        teams_dict : dict={}, position : str="") -> None:

        if position not in self.hitting_base.keys():
            return
        for player in self.hitting_base[position].keys():
            self.hitting_rating[position][player] = (
                self.hitting_base[position][player] /
                team_games_played[teams_dict[player]]
            )
