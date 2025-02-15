from .Player_Metric import Player_Metric

class Multipoint_Games(Player_Metric):

    def __init__(self):
        super().__init__('multipoint_games', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        multipoint = {}
        for player in players.keys():
            total_points = (
                players[player]['stats']['goals'] +
                players[player]['stats']['assists']
            )
            if total_points > 1:
                multipoint[player] = {self.name : 1}
            else:
                multipoint[player] = {self.name : 0}
        return multipoint
