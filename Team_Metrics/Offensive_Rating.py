class Offensive_Rating():

    POWER_PLAY_STRENGTH = 0.20
    GOALS_PER_GAME = 0.50
    SHOTS_PER_GAME = 0.30

    def __init__(self):        
        self.shots_for = {}
        self.shots_for_unscaled = {}
        self.goals_for = {}
        self.goals_for_unscaled = {}
        self.pp_goals = {}
        self.pp_oppertunities = {}
        self.pp_rating = {}
        self.games_played = {}
        self.offensive_rating = {}
        self.offensive_rating_trends = {}


    def get_dict(self) -> dict:
        return self.offensive_rating


    def get_shots_for_dict(self) -> dict:
        return self.shots_for


    def get_goals_for_dict(self) -> dict:
        return self.goals_for


    def get_pp_dict(self) -> dict:
        return self.pp_rating


    def get_trend_dict(self) -> dict:
        return self.offensive_rating_trends


    def get_pp_oppertunities_dict(self) -> dict:
        return self.pp_oppertunities


    def rating_reset(self) -> None:
        self.shots_for.clear()
        self.shots_for_unscaled.clear()
        self.goals_for.clear()
        self.goals_for_unscaled.clear()
        self.pp_goals.clear()
        self.pp_oppertunities.clear()
        self.pp_rating.clear()
        self.games_played.clear()
        self.offensive_rating.clear()
        self.offensive_rating_trends.clear()


    def get_data_set(self, match_data : dict={}) -> list:

        # place the requried data into a dictionary for later use
        shots_for_data = {}
        goals_for_data = {}
        power_play_data = {}

        # get home and away team
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        # home data
        shots_for_data[home_team] = home_team_stats["shots"]
        goals_for_data[home_team] = (
            home_team_stats["goals"] - (
                home_team_stats["empty_net_goals"] * 0.3)
        )
        power_play_data[home_team] = {
            'pp_goals_for' : (
                home_team_stats["power_play_goals"] -
                away_team_stats["short_handed_goals"]
            ),
            'pp_chances_for' : home_team_stats["power_play_chances"]
        }
        
        # away data
        shots_for_data[away_team] = away_team_stats["shots"]
        goals_for_data[away_team] = (
            away_team_stats["goals"] - (
                away_team_stats["empty_net_goals"] * 0.3)
        )
        power_play_data[away_team] = {
            'pp_goals_for' : (
                away_team_stats["power_play_goals"] -
                home_team_stats["short_handed_goals"]
            ),
            'pp_chances_for' : away_team_stats["power_play_chances"]
        }
        return {
            'shots_for' : shots_for_data,
            'goals_for' : goals_for_data,
            'power_play_data' : power_play_data
        }


    def add_match_data(self, offensive_data : dict={}) -> None:

        for team in list(offensive_data['shots_for'].keys()):
            if team in self.shots_for.keys():

                # shots for
                self.shots_for_unscaled[team] += (
                    offensive_data['shots_for'][team]
                )
                
                # goals for
                self.goals_for_unscaled[team] += (
                    offensive_data['goals_for'][team]
                )
                
                # power play
                self.pp_goals[team] += (
                    offensive_data['power_play_data'][team]['pp_goals_for']
                )
                self.pp_oppertunities[team] += (
                    offensive_data['power_play_data'][team]['pp_chances_for']
                )
                
                # games played
                self.games_played[team] += 1
            else:

                # shots for
                self.shots_for_unscaled[team] = (
                    offensive_data['shots_for'][team]
                )
                
                # goals for
                self.goals_for_unscaled[team] = (
                    offensive_data['goals_for'][team]
                )
                
                # power play
                self.pp_goals[team] = (
                    offensive_data['power_play_data'][team]['pp_goals_for']
                )
                self.pp_oppertunities[team] = (
                    offensive_data['power_play_data'][team]['pp_chances_for']
                )

                # games played
                self.games_played[team] = 1


    def calculate_all(self) -> None:
        for team in self.shots_for_unscaled.keys():

            # shots for divided by game
            self.shots_for[team] = (
                self.shots_for_unscaled[team] / self.games_played[team]
            )

            # goals for divided by game
            self.goals_for[team] = (
                self.goals_for_unscaled[team] / self.games_played[team]
            )

            # pp converted to percentage
            if self.pp_oppertunities[team] > 0:
                self.pp_rating[team] = (
                    self.pp_goals[team] / self.pp_oppertunities[team]
                )
            else:
                self.pp_rating[team] = 0.0


    def combine_metrics(self) -> None:
        for team in self.shots_for.keys():
            self.offensive_rating[team] = (
                (self.shots_for[team] *
                    self.SHOTS_PER_GAME) +
                (self.goals_for[team] *
                    self.GOALS_PER_GAME) +
                (self.pp_rating[team] *
                    self.POWER_PLAY_STRENGTH)
            )


    def update_trends(self, date : str="") -> None:
        self.offensive_rating_trends[date] = {}
        for team in self.offensive_rating.keys():
            self.offensive_rating_trends[date][team] = (
                self.offensive_rating[team]
            )
