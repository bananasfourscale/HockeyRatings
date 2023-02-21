import requests
import json
from enum import Enum

recent_form_rating = {
    'Anaheim Ducks' : 0,
    'Arizona Coyotes' : 0,
    'Boston Bruins' : 0,
    'Buffalo Sabres' : 0,
    'Calgary Flames' : 0,
    'Carolina Hurricanes' : 0,
    'Chicago Blackhawks' : 0,
    'Colorado Avalanche' : 0,
    'Columbus Blue Jackets' : 0,
    'Dallas Stars' : 0,
    'Detroit Red Wings' : 0,
    'Edmonton Oilers' : 0,
    'Florida Panthers' : 0,
    'Los Angeles Kings' : 0,
    'Minnesota Wild' : 0,
    'Montréal Canadiens' : 0,
    'Nashville Predators' : 0,
    'New Jersey Devils' : 0,
    'New York Islanders' : 0,
    'New York Rangers' : 0,
    'Ottawa Senators' : 0,
    'Philadelphia Flyers' : 0,
    'Pittsburgh Penguins' : 0,
    'San Jose Sharks' : 0,
    'Seattle Kraken' : 0,
    'St. Louis Blues' : 0,
    'Tampa Bay Lightning' : 0,
    'Toronto Maple Leafs' : 0,
    'Vancouver Canucks' : 0,
    'Vegas Golden Knights' : 0,
    'Washington Capitals' : 0,
    'Winnipeg Jets' : 0,
}

recent_form_trends = {
    'Anaheim Ducks' : [],
    'Arizona Coyotes' : [],
    'Boston Bruins' : [],
    'Buffalo Sabres' : [],
    'Calgary Flames' : [],
    'Carolina Hurricanes' : [],
    'Chicago Blackhawks' : [],
    'Colorado Avalanche' : [],
    'Columbus Blue Jackets' : [],
    'Dallas Stars' : [],
    'Detroit Red Wings' : [],
    'Edmonton Oilers' : [],
    'Florida Panthers' : [],
    'Los Angeles Kings' : [],
    'Minnesota Wild' : [],
    'Montréal Canadiens' : [],
    'Nashville Predators' : [],
    'New Jersey Devils' : [],
    'New York Islanders' : [],
    'New York Rangers' : [],
    'Ottawa Senators' : [],
    'Philadelphia Flyers' : [],
    'Pittsburgh Penguins' : [],
    'San Jose Sharks' : [],
    'Seattle Kraken' : [],
    'St. Louis Blues' : [],
    'Tampa Bay Lightning' : [],
    'Toronto Maple Leafs' : [],
    'Vancouver Canucks' : [],
    'Vegas Golden Knights' : [],
    'Washington Capitals' : [],
    'Winnipeg Jets' : [],
}


class recent_form_weights(Enum):
    LAST_TEN = 0.85
    STREAK = 0.15


def recent_form_get_dict() -> dict:
    return recent_form_rating


def recent_form_get_trend_dict() -> dict:
    return recent_form_trends


def recent_form_get_data_set(team_records : dict={}) -> list:
    last_ten_data = {}
    streak_data = {}
    for team in team_records.keys():

        # some additional shortcuts for getting data
        last_10 = team_records[team]["records"]["overallRecords"][3]
        streak = team_records[team]["streak"]

        # now use the shortcuts to actually assign the values
        streak_data[team] = (streak["streakType"], streak["streakNumber"])
        last_ten_data[team] = (last_10["wins"], last_10["ot"])
    return [last_ten_data, streak_data]


def recent_form_calculate_last_ten(last_ten : dict={}) -> dict:
    calc_last_ten = {}
    for team in last_ten.keys():
        calc_last_ten[team] = last_ten[team][0] + (last_ten[team][1] * (1 / 3))
    return calc_last_ten


def recent_form_calculate_streak(streak : dict={}) -> dict:
    calc_streak = {}
    for team in streak.keys():
        if streak[team][0] == "wins":
            calc_streak[team] = streak[team][1]
        elif streak[team][0] == "ot":
            calc_streak[team] = (streak[team][1] * (-1 / 3))
        else:
            calc_streak[team] = (streak[team][1] * -1)
    return calc_streak


def recent_form_combine_metrics(metric_list : list=[]) -> None:
    for team in recent_form_rating.keys():
        recent_form_rating[team] = \
            (metric_list[0][team] * \
                recent_form_weights.LAST_TEN.value) + \
            (metric_list[1][team] * \
                recent_form_weights.STREAK.value)


if __name__ == "__main__":

    # combine and scale wins + OT wins to get the rating form score for
    # the last ten games
    recent_form_metrics = recent_form_get_data_set()
    print("Recent Form (uncorrected):")
    for team in recent_form_rating.keys() :
        print("\t" + team + '=' + str(recent_form_rating[team]))
