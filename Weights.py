from enum import *

divisions = {
    'Anaheim Ducks' : "PAC",
    'Arizona Coyotes' : "CEN",
    'Boston Bruins' : "ATL",
    'Buffalo Sabres' : "ATL",
    'Calgary Flames' : "CEN",
    'Carolina Hurricanes' : "MET",
    'Chicago Blackhawks' : "CEN",
    'Colorado Avalanche' : "CEN",
    'Columbus Blue Jackets' : "MET",
    'Dallas Stars' : "CEN",
    'Detroit Red Wings' : "ATL",
    'Edmonton Oilers' : "PAC",
    'Florida Panthers' : "ATL",
    'Los Angeles Kings' : "PAC",
    'Minnesota Wild' : "CEN",
    'Montréal Canadiens' : "ATL",
    'Nashville Predators' : "CEN",
    'New Jersey Devils' : "MET",
    'New York Islanders' : "MET",
    'New York Rangers' : "MET",
    'Ottawa Senators' : "ATL",
    'Philadelphia Flyers' : "MET",
    'Pittsburgh Penguins' : "MET",
    'San Jose Sharks' : "PAC",
    'Seattle Kraken' : "PAC",
    'St. Louis Blues' : "CEN",
    'Tampa Bay Lightning' : "ATL",
    'Toronto Maple Leafs' : "ATL",
    'Vancouver Canucks' : "PAC",
    'Vegas Golden Knights' : "PAC",
    'Washington Capitals' : "MET",
    'Winnipeg Jets' : "CEN",
}


VERSION_MAJOR = 6
VERSION_MINOR = 4


class total_rating_weights(Enum):
    WIN_RATING_WEIGHT = 0.25
    CLUTCH_RATING_WEIGHT = 0.05
    FORM_RATING_WEIGHT = 0.10
    SOS_RATING_WEIGHT = 0.25
    OFFENSIVE_RATING_WEIGHT = 0.15
    DEFENSIVE_RATING_WEIGHT = 0.20


class goalie_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.30
    WIN_RATING_WEIGHT = 0.10
    SAVE_PERCENTAGE_WEIGHT = 0.40
    GOALS_AGAINST_WEIGHT = 0.20

class defensemen_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.35
    HITS_WEIGHT = 0.05
    DISIPLINE_WEIGHT = 0.25
    SHOT_BLOCKING_WEIGHT = 0.10
    PLUS_MINUS_WEIGHT = 0.05
    POINTS_WEIGHT = 0.20

class forward_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.25
    POINTS_WEIGHT = 0.30
    PLUS_MINUS_WEIGHT = 0.05
