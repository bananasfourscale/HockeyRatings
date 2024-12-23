class Goals_Against():

    def __init__(self):
        self.goalie_goals_against_base = {}
        self.goalie_goals_against_rating = {}


    def get_dict(self) -> dict:
        return self.goalie_goals_against_rating


    def rating_reset(self) -> None:
        self.goalie_goals_against_base.clear()
        self.goalie_goals_against_rating.clear()


    def get_data_set(self, match_data : dict={}) -> dict:
        goals_against = {}
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
            goals_against[goalie] = shot_total - save_total
        return goals_against


    def add_match_data(self,
        goalie_goals_against_data : dict={}) -> None:

        for goalie in goalie_goals_against_data.keys():
            if goalie in self.goalie_goals_against_base.keys():
                self.goalie_goals_against_base[goalie] += (
                    goalie_goals_against_data[goalie]
                )
            else:
                self.goalie_goals_against_base[goalie] = (
                    goalie_goals_against_data[goalie]
                )
            if goalie == 'Andrei Vasilevskiy':
                print(self.goalie_goals_against_base[goalie])


    def scale_by_utilization(self,
        goalie_utilization : dict={}) -> None:

        tuple_list = []
        for team, rating in goalie_utilization.items():
            tuple_list.append(tuple((team, rating)))
            tuple_list.sort(key = lambda x: x[1], reverse=True)
        for count in range(0, len(tuple_list), 1):
            goalie_name = tuple_list[count][0]
            self.goalie_goals_against_rating[goalie_name] = (
                (self.goalie_goals_against_base[goalie_name] + 1) *
                ((count + 1) / len(tuple_list))
            )
        # for goalie in goalie_goals_against_base.keys():
        #     goalie_goals_against_rating[goalie] = (
        #         (goalie_goals_against_base[goalie] + 1) *
        #         (1 - goalie_utilization[goalie])
        #     )
