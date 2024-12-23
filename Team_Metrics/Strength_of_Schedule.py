class Strength_of_Schedule():

    # weights
    WIN_REGULATION_WEIGHT = 1.0
    LOSE_REGULATION_WEIGHT = 0.0
    WIN_OT_WEIGHT = 0.33
    LOSE_OT_WEIGHT = 0.10
    WIN_SO_WEIGHT = 0.10
    LOSE_SO_WEIGHT = 0.05

    # match indecies
    AWAY_TEAM = 0
    AWAY_SCORE = 1
    HOME_TEAM = 2
    HOME_SCORE = 3
    EXTRA_TIME = 4

    def __init__(self):
        self.strength_of_schedule = {}
        self.strength_of_schedule_games_played = {}
        self.sos_rating = {}
        self.strength_of_schedule_trends = {}


    def get_dict(self) -> dict:
        return self.sos_rating


    def get_games_played_dict(self) -> dict:
        return self.strength_of_schedule_games_played


    def get_trend_dict(self) -> dict:
        return self.strength_of_schedule_trends


    def rating_reset(self) -> None:
        self.strength_of_schedule.clear()
        self.strength_of_schedule_games_played.clear()
        self.sos_rating.clear()
        self.strength_of_schedule_trends.clear()


    def get_data_set(self, match_data : dict={}) -> dict:
        game_value = {}
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]
        home_score_final = (
            home_team_stats["first_period_goals"] +
            home_team_stats["second_period_goals"] +
            home_team_stats["third_period_goals"] +
            home_team_stats["OT_goals"] +
            home_team_stats["SO_goals"]
        )
        away_score_final = (
            away_team_stats["first_period_goals"] +
            away_team_stats["second_period_goals"] +
            away_team_stats["third_period_goals"] +
            away_team_stats["OT_goals"] +
            away_team_stats["SO_goals"]
        )
        final_game_state = match_data['game_stats']['result']

        # determine who won and lost the game
        if home_score_final > away_score_final:
            winner = home_team
            loser = away_team
        else:
            winner = away_team
            loser = home_team

        # now give points between 0 and 1 to each team
        # depending on the game result
        if final_game_state == "REG":
            game_value[winner] = \
                self.WIN_REGULATION_WEIGHT
            game_value[loser] = \
                self.LOSE_REGULATION_WEIGHT
        elif final_game_state == "OT":
            game_value[winner] = (
                self.WIN_OT_WEIGHT
            )
            game_value[loser] = (
                self.LOSE_OT_WEIGHT
            )
        else:
            game_value[winner] = (
                self.WIN_SO_WEIGHT
            )
            game_value[loser] = (
                self.LOSE_SO_WEIGHT
            )
        return game_value


    def add_match_data(self, sos_data : dict={}) -> None:
        for team in sos_data.keys():
            
            # add games played and sos data for each team to be scaled later
            if team in self.strength_of_schedule_games_played.keys():
                self.strength_of_schedule_games_played[team] += 1
                self.strength_of_schedule[team] += sos_data[team]
            else:
                self.strength_of_schedule_games_played[team] = 1
                self.strength_of_schedule[team] = sos_data[team]


    def scale_by_games(self) -> None:

        # place the requried data into a dictionary for later use
        for team in self.strength_of_schedule.keys():
            self.sos_rating[team] = (
                self.strength_of_schedule[team] /
                self.strength_of_schedule_games_played[team]
            )


    def update_trends(self, date : str="") -> None:
        self.strength_of_schedule_trends[date] = {}
        for team in self.sos_rating.keys():
            self.strength_of_schedule_trends[date][team] = self.sos_rating[team]
