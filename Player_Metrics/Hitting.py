from .Player_Metric import Player_Metric

class Hitting(Player_Metric):

    def __init__(self):
        super().__init__('hitting', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        hitting = {}
        for player in players.keys():
            hitting[player] = {
                self.name : players[player]['stats']['hits'] -
                    (players[player]['stats']['hits_taken'] * 0.25)
            }
        return hitting
