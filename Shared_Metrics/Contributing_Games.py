class Contributing_Games():    

    def __init__(self):
        self.contribution_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.contribution_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.comparator = 'total'


    def get_base_dict(self, position : str="") -> dict:
        if position in self.contribution_base.keys():
            return self.contribution_base[position]
        return {}
        

    def get_dict(self, position : str="") -> dict:
        if position in self.contribution_rating.keys():
            return self.contribution_rating[position]
        return {}
        

    def rating_reset(self) -> None:
        for key in self.contribution_base.keys():
            self.contribution_base[key].clear()
        for key in self.contribution_rating.keys():
            self.contribution_rating[key].clear()


    def get_comparator(self):
        return self.comparator
        

    def get_data_set(self, players : dict={}) -> dict:
        contributing_games = {}
        for player in players.keys():
            total_points = (
                players[player]['stats']['goals'] +
                players[player]['stats']['assists']
            )

            # if they score this game then 1 otherwise 0
            if total_points >= 1:
                contributing_games[player] = {'contributing_games' : 1}
            else:
                contributing_games[player] = {'contributing_games' : 0}
        return contributing_games


    def add_match_data(self, contribution_data : dict={},
        position : str="") -> None:
        if position not in self.contribution_base.keys():
            return {}
        for player in contribution_data.keys():
            if player in self.contribution_base[position].keys():
                self.contribution_base[position][player] += \
                    contribution_data[player]['contributing_games']
            else:
                self.contribution_base[position][player] = \
                    contribution_data[player]['contributing_games']


    def scale_by_games(self, team_games_played : dict={},
        teams_dict : dict={}, position : str="") -> None:
        if position not in self.contribution_base.keys():
            return
        for player in self.contribution_base[position].keys():
            self.contribution_rating[position][player] = (
                self.contribution_base[position][player] /
                team_games_played[teams_dict[player]]
            )
