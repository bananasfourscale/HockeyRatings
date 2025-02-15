from .Player_Metric import Player_Metric

class Total_Points(Player_Metric):

    def __init__(self):
        super().__init__('total_points', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        total_points = {}
        for player in players.keys():
            total_points[player] = {
                self.name : (
                    (players[player]['stats']['goals']) +
                    (players[player]['stats']['primary_assist'] * 0.90) +
                    (players[player]['stats']['secondary_assist'] * 0.85)
                )
            }
        return total_points
