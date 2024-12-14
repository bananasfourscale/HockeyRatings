from enum import Enum
from Team_Metrics.Clutch import Clutch

class Metric_Order(Enum):
    CLUTCH = 0
    DEFENSIVE = 1
    OFFENSIVE = 2
    RECENT = 3
    SOS = 4
    TOTAL = 5


class Game_Parser():

    HOME_INDEX = 0
    AWAY_INDEX = 1
    
    def __init__(self):
        pass


    def parse_team_match_data(self, clutch : Clutch=None, match_data : dict={},
        relative_metrics : list=[]) -> list:

        metric_data = {"team_data" : {}}

        # get home and away team
        away_team = match_data["game_stats"]["away_team"]
        home_team = match_data["game_stats"]["home_team"]

        ### clutch rating ###
        clutch_data = clutch.get_data_set(match_data)
        clutch_data[home_team] *= (
            1 + relative_metrics[Metric_Order.CLUTCH.value][
                self.AWAY_INDEX]
        )
        clutch_data[away_team] *= (
            1 + relative_metrics[Metric_Order.CLUTCH.value][
                self.HOME_INDEX]
        )
        metric_data['team_data']['clutch_data'] = clutch_data

        ### defensive rating ###
        # shots against
        defensive_data = defensive_rating_get_data_set(match_data)
        defensive_data['shots_against'][home_team] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.AWAY_INDEX]
        )
        defensive_data['shots_against'][away_team] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.HOME_INDEX]
        )

        # goals against
        defensive_data['goals_against'][home_team] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.AWAY_INDEX]
        )
        defensive_data['goals_against'][away_team] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.HOME_INDEX]
        )

        # penalty kill goals against
        defensive_data['penalty_kill_data'][home_team]['pk_goals_against'] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.AWAY_INDEX]
        )
        defensive_data['penalty_kill_data'][away_team]['pk_goals_against'] /= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.HOME_INDEX]
        )
        metric_data['team_data']['defensive_data'] = defensive_data

        ### offensive rating ###
        # shots for
        offensive_data = offensive_rating_get_data_set(match_data)
        offensive_data['shots_for'][home_team] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.AWAY_INDEX]
        )
        offensive_data['shots_for'][away_team] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.HOME_INDEX]
        )

        # goals for
        offensive_data['goals_for'][home_team] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.AWAY_INDEX]
        )
        offensive_data['goals_for'][away_team] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.HOME_INDEX]
        )

        # power play goals for
        offensive_data['power_play_data'][home_team]['pp_goals_for'] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.AWAY_INDEX]
        )
        offensive_data['power_play_data'][away_team]['pp_goals_for'] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.HOME_INDEX]
        )
        metric_data['team_data']['offensive_data'] = offensive_data

        ### recent form ###
        recent_form_data = recent_form_get_data_set(match_data)
        recent_form_data['game value'][home_team] *= (
            1 + relative_metrics[Metric_Order.RECENT.value][
                self.AWAY_INDEX]
        )
        recent_form_data['game value'][away_team] *= (
            1 + relative_metrics[Metric_Order.RECENT.value][
                self.HOME_INDEX]
        )
        metric_data['team_data']['recent_form_data'] = recent_form_data

        ### strength of schedule
        sos_data = strength_of_schedule_get_data_set(match_data)
        sos_data[home_team] *= (
            1 + relative_metrics[Metric_Order.SOS.value][self.AWAY_INDEX]
        )
        sos_data[away_team] *= (
            1 + relative_metrics[Metric_Order.SOS.value][self.HOME_INDEX]
        )
        metric_data['team_data']['sos_data'] = sos_data

        ### discipline
        discipline_data = discipline_get_team_data_set(match_data)
        discipline_data[home_team]['penalties_taken'] *= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.AWAY_INDEX]
        )
        discipline_data[home_team]['penalties_drawn'] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.AWAY_INDEX]
        )
        discipline_data[home_team]['penalty_net_minutes'] = (
            discipline_data[home_team]['penalties_taken'] -
            discipline_data[home_team]['penalties_drawn']
        )
        discipline_data[away_team]['penalties_taken'] *= (
            1 + relative_metrics[Metric_Order.OFFENSIVE.value][
                self.HOME_INDEX]
        )
        discipline_data[away_team]['penalties_drawn'] *= (
            1 + relative_metrics[Metric_Order.DEFENSIVE.value][
                self.HOME_INDEX]
        )
        discipline_data[away_team]['penalty_net_minutes'] = (
            discipline_data[away_team]['penalties_taken'] -
            discipline_data[away_team]['penalties_drawn']
        )
        # return the list of all metric data for this match
        return metric_data