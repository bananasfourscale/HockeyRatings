class Total_Points():

    def __init__(self):
        self.total_points_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.total_points_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }


    def get_base_dict(self, position : str="") -> dict:
        if position in self.total_points_base.keys():
            return self.total_points_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.total_points_rating.keys():
            return self.total_points_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.total_points_base.keys():
            self.total_points_base[key].clear()
        for key in self.total_points_rating.keys():
            self.total_points_rating[key].clear()


    def get_data_set(self, players : dict={}) -> dict:
        total_points = {}
        for player in players.keys():
            total_points[player] = {
                'total_points' : (
                    (players[player]['stats']['goals']) +
                    (players[player]['stats']['primary_assist'] * 0.90) +
                    (players[player]['stats']['secondary_assist'] * 0.85)
                )
            }
        return total_points


    def add_match_data(self, total_points_data : dict={},
        position : str="") -> None:

        if position not in self.total_points_base.keys():
            return {}
        for player in total_points_data.keys():
            if player in self.total_points_base[position].keys():
                self.total_points_base[position][player] += (
                    total_points_data[player]["total_points"]
                )
            else:
                self.total_points_base[position][player] = (
                    total_points_data[player]["total_points"]
                )
                    

    def scale_by_games(self, team_games_played : dict={},
        teams_dict : dict={}, position : str="") -> None:

        if position not in self.total_points_base.keys():
            return
        for player in self.total_points_base[position].keys():
            self.total_points_rating[position][player] = (
                self.total_points_base[position][player] /
                team_games_played[teams_dict[player]]
            )
