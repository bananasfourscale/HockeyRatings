from .Player_Metric import Player_Metric

class Blocked_Shots(Player_Metric):

    def __init__(self):
        super().__init__('blocked_shots', 'shot_differential')


    def get_data_set(self, players : dict={}) -> dict:
        blocks = {}
        for player in players.keys():
            blocks[player] = {self.name : players[player]['stats']['blocks']}
        return blocks
    

    def scale_rating(self, position : str="C", external_scalar_metric : dict={},
        teams_dict : dict={}) :

        for player in self.base_rating[position].keys():
            self.final_rating[position][player] = (
                self.base_rating[position][player] /
                external_scalar_metric[teams_dict[player]]
            )
