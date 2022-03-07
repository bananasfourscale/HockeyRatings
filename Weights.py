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
    'Montreal Canadiens' : "ATL",
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


VERSION_MAJOR = 5
VERSION_MINOR = 0

class total_rating_weights(Enum):
    WIN_RATING_WEIGHT = 0.5
    SCORING_RATING_WEIGHT = 0.05
    SPECIAL_TEAMS_RATING_WEIGHT = 0.08
    CLUTCH_RATING_WEIGHT = 0.12
    FORM_RATING_WEIGHT = 0.12
    SOS_RATING_WEIGHT = 0.13