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
    'Phoenix Coyotes' : "CEN",
    'Atlanta Thrashers' : "MET",
    'Winnipeg Jets (1979)' : "CEN",
    'Hartford Whalers' : "MET",
    'Quebec Nordiques' : "CEN",
    'Minnesota North Stars' : "CEN",
    'Colorado Rockies' : "CEN",
    'Atlanta Flames' : "MET",
    'Kansas City Scouts' : "CEN",
    'California Golden Seals' : "PAC",
    'Oakland Seals' : "PAC",
    'Cleveland Barons' : "CEN",
}


VERSION_MAJOR = 7
VERSION_MINOR = 0

EYE_TEST_WEIGHT = 0.50

class total_rating_weights(Enum):
    CLUTCH_RATING_WEIGHT = 0.05
    DEFENSIVE_RATING_WEIGHT = 0.25
    OFFENSIVE_RATING_WEIGHT = 0.20
    RECENT_FORM_RATING_WEIGHT = 0.25
    SOS_RATING_WEIGHT = 0.25


class goalie_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.30
    SAVE_PERCENTAGE_WEIGHT = 0.40
    GOALS_AGAINST_WEIGHT = 0.10
    SAVE_CONSISTENCY_WEIGHT = 0.20


class forward_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.30
    HITS_WEIGHT = 0.05
    DISIPLINE_WEIGHT = 0.05
    SHOT_BLOCKING_WEIGHT = 0.03
    PLUS_MINUS_WEIGHT = 0.02
    POINTS_WEIGHT = 0.25
    TAKEAWAYS_WEIGHT = 0.05
    CONTRIBUTION_WEIGHT = 0.15
    MULTIPOINT_WEIGHT = 0.10


class defensemen_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.25
    HITS_WEIGHT = 0.10
    DISIPLINE_WEIGHT = 0.05
    SHOT_BLOCKING_WEIGHT = 0.10
    PLUS_MINUS_WEIGHT = 0.10
    POINTS_WEIGHT = 0.25
    TAKEAWAYS_WEIGHT = 0.15
