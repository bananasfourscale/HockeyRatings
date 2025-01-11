class Multipoint_Games():

    def __init__(self):
        self.multipoint_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.multipoint_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.comparator = 'total'


    def get_base_dict(self, position : str="") -> dict:
        if position in self.multipoint_base.keys():
            return self.multipoint_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.multipoint_rating.keys():
            return self.multipoint_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.multipoint_base.keys():
            self.multipoint_base[key].clear()
        for key in self.multipoint_rating.keys():
            self.multipoint_rating[key].clear()


    def get_comparator(self):
        return self.comparator


    def get_data_set(self, players : dict={}) -> dict:
        multipoint = {}
        for player in players.keys():
            total_points = (
                players[player]['stats']['goals'] +
                players[player]['stats']['assists']
            )
            if total_points > 1:
                multipoint[player] = {'multipoint_games' : 1}
            else:
                multipoint[player] = {'multipoint_games' : 0}
        return multipoint


    def add_match_data(self, multipoint_data : dict={},
        position : str="") -> None:

        if position not in self.multipoint_base.keys():
            return {}
        for player in multipoint_data.keys():
            if player in self.multipoint_base[position].keys():
                self.multipoint_base[position][player] += (
                    multipoint_data[player]["multipoint_games"]
                )
            else:
                self.multipoint_base[position][player] = (
                    multipoint_data[player]["multipoint_games"]
                )
                

    def scale_by_games(self, team_games_played : dict={},
        teams_dict : dict={}, position : str="") -> None:

        if position not in self.multipoint_base.keys():
            return
        for player in self.multipoint_base[position].keys():
            self.multipoint_rating[position][player] = (
                self.multipoint_base[position][player] /
                team_games_played[teams_dict[player]]
            )
