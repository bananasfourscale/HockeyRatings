from .Player_Metric import Player_Metric

class Utilization(Player_Metric):

    def __init__(self):
        super().__init__('utilization', 'total')


    def get_data_set(self, players : dict={}) -> dict: 
        utilization = {}
        for player in players.keys():

            # convert time on ice to minutes
            time_on_ice = (
                float(
                    players[player]['stats']['time_on_ice'].split(":")[0]) +
                float(
                    players[player]['stats']['time_on_ice'].split(":")[1]) / 60
            )
            utilization[player] = {
                self.name : time_on_ice,
                'team' : players[player]['team']
            }
        return utilization
    

    # def add_match_data(self, data_set = ..., position = "C"):
    #     connor_flag = False
    #     if position == "G":
    #         for goalie in data_set.keys():
    #             if goalie == "Connor Hellebuyck":
    #                 connor_flag = True
    #                 print("game data")
    #                 print(data_set[goalie][self.name])
    #     super().add_match_data(data_set, position)
    #     if connor_flag:
    #         print("base total")
    #         print(self.base_rating["G"]["Connor Hellebuyck"])

