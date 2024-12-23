class Discipline():

    def __init__(self):
        self.discipline_base = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.discipline_rating = {
            'G' : {},
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }


    def get_base_dict(self, position : str="") -> dict:
        if position in self.discipline_base.keys():
            return self.discipline_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.discipline_rating.keys():
            return self.discipline_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.discipline_base.keys():
            self.discipline_base[key].clear()
        for key in self.discipline_rating.keys():
            self.discipline_rating[key].clear()


    def get_data_set(self, players : dict={}) -> dict:
        discipline = {}
        for player in players.keys():
            discipline[player] = {
                'penalties_taken' : 
                    players[player]['stats']['penalty_minutes'],
                'penalties_drawn' : 
                    players[player]['stats']['penalty_minutes_drawn']
            }
        return discipline


    # def get_data_set(self, match_data : dict={}) -> dict:
    #     discipline = {}
    #     team_list = [match_data['game_stats']['home_team'],
    #         match_data['game_stats']['away_team']]
    #     for team in team_list:
    #         discipline[team] = {
    #             'penalties_taken' : 
    #                 match_data['game_stats'][team]["team_stats"][
    #                     'penalty_minutes'],
    #             'penalties_drawn' :
    #                 match_data['game_stats'][team]["team_stats"][
    #                     'penalties_drawn']
    #         }
    #     return discipline


    def add_match_data(self, discipline_data : dict = {},
        position : str="") -> None:

        if position not in self.discipline_base.keys():
            return {}
        for player in discipline_data.keys():
            if player in self.discipline_base[position].keys():
                self.discipline_base[position][player] += \
                    discipline_data[player]["penalty_net_minutes"]
            else:
                self.discipline_base[position][player] = \
                    discipline_data[player]["penalty_net_minutes"]
                    

    def scale_by_utilization(self, utilization : dict={},
            position : str="") -> None:
        if position not in self.discipline_base.keys():
            return
        for player in self.discipline_base[position].keys():
            self.discipline_rating[position][player] = (
                self.discipline_base[position][player] *
                (1 - utilization[player])
            )
