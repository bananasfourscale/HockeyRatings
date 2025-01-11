class Save_Consistency():

    def __init__(self):
        self.goalie_save_consistency_base = {}
        self.goalie_save_consistency_rating = {}
        self.comparator = 'total'


    def get_dict(self) -> dict:
        return self.goalie_save_consistency_rating


    def rating_reset(self) -> None:
        self.goalie_save_consistency_base.clear()
        self.goalie_save_consistency_rating.clear()


    def get_comparator(self):
        return self.comparator


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
                save_consistency[goalie] = 1
            else:
                save_consistency[goalie] = 0
        return save_consistency


    def add_match_data(self, goalie_save_consistency_data : dict={}) -> None:

        for goalie in goalie_save_consistency_data.keys():
            if goalie in self.goalie_save_consistency_base.keys():
                self.goalie_save_consistency_base[goalie] += (
                    goalie_save_consistency_data[goalie]
                )
            else:
                self.goalie_save_consistency_base[goalie] = (
                    goalie_save_consistency_data[goalie]
                )
                

    def scale_by_games(self, teams_games_played : dict={},
        goalie_teams_dict : dict={}) -> None:

        for goalie in self.goalie_save_consistency_base.keys():
            self.goalie_save_consistency_rating[goalie] = (
                self.goalie_save_consistency_base[goalie] /
                teams_games_played[goalie_teams_dict[goalie]]
            )
