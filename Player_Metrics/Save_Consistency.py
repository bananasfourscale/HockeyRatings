from .Player_Metric import Player_Metric

class Save_Consistency(Player_Metric):

    def __init__(self):
        super().__init__('save_consistency', 'total')


    def get_data_set(self, match_data : dict={}) -> dict:

        save_consistency = {}
        for goalie in match_data.keys():
            shot_total = (
                match_data[goalie]['stats']["even_shots"] + 
                match_data[goalie]['stats']["power_play_shots"] + 
                match_data[goalie]['stats']["short_handed_shots"]
            )
            save_total = (
                match_data[goalie]['stats']["even_saves"] + 
                match_data[goalie]['stats']["power_play_saves"] + 
                match_data[goalie]['stats']["short_handed_saves"]
            )
            if shot_total > 0:
                save_consistency_game = save_total / shot_total
            else:
                save_consistency_game = 0

            # a game with 90%+ save per is considered standard.
            if save_consistency_game > 0.9:
                save_consistency[goalie] = {self.name: 1}
            else:
                save_consistency[goalie] = {self.name: 0}
        return save_consistency
