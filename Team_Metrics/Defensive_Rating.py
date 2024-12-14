class Defensive_Rating():

    PENALTY_KILL_STRENGTH = 0.20
    GOALS_AGAINST_PER_GAME = 0.50
    SHOTS_AGAINST_PER_GAME = 0.30

    def __init__(self):
        self.shots_against = {}
        self.shots_against_unscaled = {}
        self.goals_against = {}
        self.goals_against_unscaled = {}
        self.pk_goals_against = {}
        self.pk_oppertunities = {}
        self.pk_rating = {}
        self.games_played = {}
        self.defensive_rating = {}
        self.defensive_rating_trends = {}


    def defensive_rating_get_dict(self) -> dict:
        return self.defensive_rating


    def defensive_rating_get_shots_against_dict(self) -> dict:
        return self.shots_against


    def defensive_rating_get_unscaled_shots_against_dict(self) -> dict:
        return self.shots_against_unscaled


    def defensive_rating_get_goals_against_dict(self) -> dict:
        return self.goals_against


    def defensive_rating_get_pk_dict(self) -> dict:
        return self.pk_rating


    def defensive_rating_get_trend_dict(self) -> dict:
        return self.defensive_rating_trends


    def defensive_rating_get_pk_oppertunities_dict(self) -> dict:
        return self.pk_oppertunities


    def defensive_rating_reset(self) -> None:
        self.shots_against.clear()
        self.shots_against_unscaled.clear()
        self.goals_against.clear()
        self.goals_against_unscaled.clear()
        self.pk_goals_against.clear()
        self.pk_oppertunities.clear()
        self.pk_rating.clear()
        self.games_played.clear()
        self.defensive_rating.clear()
        self.defensive_rating_trends.clear()

    def defensive_rating_get_data_set(self, match_data : dict={}) -> list:

        # place the requried data into a dictionary for later use
        shots_against_data = {}
        goals_against_data = {}
        penalty_kill_data = {}

        # get home and away team
        home_team = match_data['game_stats']['home_team']
        home_team_stats = match_data['game_stats'][home_team]["team_stats"]
        away_team = match_data['game_stats']['away_team']
        away_team_stats = match_data['game_stats'][away_team]["team_stats"]

        # home data
        shots_against_data[home_team] = away_team_stats["shots"]
        goals_against_data[home_team] = (
            away_team_stats["goals"] - (
                away_team_stats["empty_net_goals"] * 0.3)
        )
        penalty_kill_data[home_team] = {
            'pk_goals_against' : (
                away_team_stats["power_play_goals"] -
                home_team_stats["short_handed_goals"]
            ),
            'pk_chances_against' : away_team_stats["power_play_chances"]
        }

        # away data
        shots_against_data[away_team] = home_team_stats["shots"]
        goals_against_data[away_team] = (
            home_team_stats["goals"] - (
                home_team_stats["empty_net_goals"] * 0.3)
        )
        penalty_kill_data[away_team] = {
            'pk_goals_against' : (
                home_team_stats["power_play_goals"] - 
                away_team_stats["short_handed_goals"]
            ),
            'pk_chances_against' : home_team_stats["power_play_chances"]
        }
        return {
            'shots_against' : shots_against_data,
            'goals_against' : goals_against_data,
            'penalty_kill_data' : penalty_kill_data
        }


    def defensive_rating_add_match_data(self, defensive_data : list=[]) -> None:
        for team in list(defensive_data['shots_against'].keys()):
            if team in self.shots_against_unscaled.keys():

                # shots against
                self.shots_against_unscaled[team] += (
                    defensive_data['shots_against'][team]
                )
                
                # goals against
                self.goals_against_unscaled[team] += (
                    defensive_data['goals_against'][team]
                )
                
                # penalty kill
                self.pk_goals_against[team] += (
                    defensive_data['penalty_kill_data'][team][
                        'pk_goals_against']
                )
                self.pk_oppertunities[team] += (
                    defensive_data['penalty_kill_data'][team][
                        'pk_chances_against']
                )
                
                # games played
                self.games_played[team] += 1
            else:

                # shots against
                self.shots_against_unscaled[team] = (
                    defensive_data['shots_against'][team]
                )
                
                # goals against
                self.goals_against_unscaled[team] = (
                    defensive_data['goals_against'][team]
                )
                
                # penalty kill
                self.pk_goals_against[team] = (
                    defensive_data['penalty_kill_data'][team][
                        'pk_goals_against']
                )
                self.pk_oppertunities[team] = (
                    defensive_data['penalty_kill_data'][team][
                        'pk_chances_against']
                )
                
                # games played
                self.games_played[team] = 1


    def defensive_rating_calculate_all(self) -> None:
        for team in self.shots_against_unscaled.keys():

            # shots against divided by game
            self.shots_against[team] = (
                self.shots_against_unscaled[team] / self.games_played[team])

            # goals against divided by game
            self.goals_against[team] = (
                self.goals_against_unscaled[team] / self.games_played[team])

            # pk converted to percentage
            if self.pk_oppertunities[team] > 0:
                self.pk_rating[team] = (
                    1.0 - (self.pk_goals_against[team] /
                        self.pk_oppertunities[team])
                )
            else:
                self.pk_rating[team] = 0.0


    def defensive_rating_combine_metrics(self) -> None:
        for team in self.shots_against.keys():
            self.defensive_rating[team] = (
                (self.shots_against[team] *
                    self.SHOTS_AGAINST_PER_GAME) +
                (self.goals_against[team] *
                    self.GOALS_AGAINST_PER_GAME) +
                (self.pk_rating[team] *
                    self.PENALTY_KILL_STRENGTH)
            )


    def defensive_rating_update_trends(self, date : str="") -> None:
        self.defensive_rating_trends[date] = {}
        for team in self.defensive_rating.keys():
            self.defensive_rating_trends[date][team] = (
                self.defensive_rating[team]
            )
