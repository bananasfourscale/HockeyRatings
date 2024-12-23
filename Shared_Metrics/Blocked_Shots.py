class Blocked_Shots():

    def __init__(self):
        self.blocks_base_forward = {}
        self.blocks_rating_forward = {}
        self.blocks_base_defense = {}
        self.blocks_rating_defense = {}
        self.blocks_base = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }
        self.blocks_rating = {
            'D' : {},
            'C' : {},
            'L' : {},
            'R' : {},
        }


    def get_base_dict(self, position : str="") -> dict:
        if position in self.blocks_base.keys():
            return self.blocks_base[position]
        return {}


    def get_dict(self, position : str="") -> dict:
        if position in self.blocks_rating.keys():
            return self.blocks_rating[position]
        return {}


    def rating_reset(self) -> None:
        for key in self.blocks_base.keys():
            self.blocks_base[key].clear()
        for key in self.blocks_rating.keys():
            self.blocks_rating[key].clear()


    def get_data_set(self, players : dict={}) -> dict:
        blocks = {}
        for player in players.keys():
            blocks[player] = {'blocks' : players[player]['stats']['blocks']}
        return blocks


    def add_match_data(self, blocks_data : dict={}, position : str="") \
                                                                        -> None:
        if position not in self.blocks_base.keys():
            return {}
        for player in blocks_data.keys():
            if player in self.blocks_base[position].keys():
                self.blocks_base[position][player] += (
                    blocks_data[player]['blocks']
                )
            else:
                self.blocks_base[position][player] = (
                    blocks_data[player]['blocks']
                )


    def scale_by_shots_against(self, team_shots_against : dict={},
        teams_dict : dict={}, position : str="") -> None:
        if position not in self.blocks_base.keys():
            return
        for player in self.blocks_base[position].keys():
            self.blocks_rating[position][player] = (
                self.blocks_base[position][player] /
                team_shots_against[teams_dict[player]]
            )
