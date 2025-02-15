from .Player_Metric import Player_Metric

class PlusMinus(Player_Metric):

    def __init__(self):
        super().__init__('plus_minus', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        plus_minus = {}
        for player in players.keys():

            # convert time on ice to minutes
            plus_minus[player] = {
                self.name : players[player]['stats']['plus_minus']
            }
        return plus_minus
