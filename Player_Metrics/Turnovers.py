from .Player_Metric import Player_Metric

class Turnovers(Player_Metric):

    def __init__(self):
        super().__init__('turnovers', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        turnovers = {}
        for player in players.keys():
            turnovers[player] = {
                self.name : (
                    players[player]['stats']['takeaways'] -
                    players[player]['stats']['giveaways']
                )
            }
        return turnovers
