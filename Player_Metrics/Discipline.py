from .Player_Metric import Player_Metric

class Discipline(Player_Metric):

    def __init__(self):
        super().__init__('discipline', 'total')


    def get_data_set(self, players : dict={}) -> dict:
        discipline = {}
        for player in players.keys():
            discipline[player] = {
                self.name :
                (players[player]['stats']['penalty_minutes_drawn'] -
                    players[player]['stats']['penalty_minutes'])
            }
        return discipline
