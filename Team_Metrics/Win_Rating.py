import requests
import json
from enum import Enum

win_rating = {
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


class win_rating_weights(Enum):
    REG_WIN = 100.0
    OT_WIN = 66.666
    OT_LOSSES = 33.333
    SHOOTOUT_WIN = 10.0


def win_rating_get_dict() -> dict:
    return win_rating


def win_rating_get_data(team_records : dict={}) -> dict:
    win_rating_data = {}
    for team in team_records.keys():
        
        games_played = team_records[team]["gamesPlayed"]
        shootout_wins = team_records[team]["records"]["overallRecords"][2]["wins"]
        regulation_wins = team_records[team]["regulationWins"]
        overtime_wins = team_records[team]["leagueRecord"]["wins"] - \
            (regulation_wins + shootout_wins)
        overtime_loses = team_records[team]["leagueRecord"]["ot"]

        # use the team name to sort the row data into the dictionary
        win_rating_data[team_records[team]["team"]["name"]] = [
            games_played, regulation_wins, overtime_wins, overtime_loses,
            shootout_wins
        ]
    return win_rating_data


def win_rating_calculate(team_records : dict={}) -> None:
    win_record_data = win_rating_get_data(team_records)
    for team in win_rating.keys():

        # apply all weights based on the type of win/loss
        win_rating[team] += float(win_record_data[team][1]) * \
            win_rating_weights.REG_WIN.value
        win_rating[team] += float(win_record_data[team][2]) * \
            win_rating_weights.OT_WIN.value
        win_rating[team] += float(win_record_data[team][3]) * \
            win_rating_weights.OT_LOSSES.value
        win_rating[team] += float(win_record_data[team][4]) * \
            win_rating_weights.SHOOTOUT_WIN.value
        win_rating[team] /= float(win_record_data[team][0])
        win_rating[team] /= 100.0
    return
