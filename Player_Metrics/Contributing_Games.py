from .Player_Metric import Player_Metric

class Contributing_Games(Player_Metric):    

    def __init__(self):
        super().__init__('contributing_games', 'total')

    def get_data_set(self, players : dict={}) -> dict:
        contributing_games = {}
        for player in players.keys():
            total_points = (
                players[player]['stats']['goals'] +
                players[player]['stats']['assists']
            )

            # if they score this game then 1 otherwise 0
            if total_points >= 1:
                contributing_games[player] = {self.name : 1}
            else:
                contributing_games[player] = {self.name : 0}
        return contributing_games
