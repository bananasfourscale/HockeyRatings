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
    

    def scale_rating(self, position : str="C",
        external_scalar_metric : dict={}, teams_dict : dict={}) -> None:
        
        for player in self.base_rating[position].keys():
            self.final_rating[position][player] = (
                self.base_rating[position][player] /
                1 + external_scalar_metric[teams_dict[player]]
            )


