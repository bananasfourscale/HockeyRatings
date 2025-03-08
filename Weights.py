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
    'Ducks' : "PAC",
    'Coyotes' : "CEN",
    'Bruins' : "ATL",
    'Sabres' : "ATL",
    'Flames' : "CEN",
    'Hurricanes' : "MET",
    'Blackhawks' : "CEN",
    'Avalanche' : "CEN",
    'Blue Jackets' : "MET",
    'Stars' : "CEN",
    'Red Wings' : "ATL",
    'Oilers' : "PAC",
    'Panthers' : "ATL",
    'Kings' : "PAC",
    'Wild' : "CEN",
    'Canadiens' : "ATL",
    'Predators' : "CEN",
    'Devils' : "MET",
    'Islanders' : "MET",
    'Rangers' : "MET",
    'Senators' : "ATL",
    'Flyers' : "MET",
    'Penguins' : "MET",
    'Sharks' : "PAC",
    'Kraken' : "PAC",
    'Blues' : "CEN",
    'Lightning' : "ATL",
    'Maple Leafs' : "ATL",
    'Canucks' : "PAC",
    'Golden Knights' : "PAC",
    'Capitals' : "MET",
    'Jets' : "CEN",
    'Utah Hockey Club' : "CEN",
}


VERSION_MAJOR = 7
VERSION_MINOR = 0

EYE_TEST_WEIGHT = 0.01

class total_rating_weights(Enum):
    CLUTCH_RATING_WEIGHT = 0.05
    GOAL_DIFF_WEIGHT = 0.15
    PENALTY_KILL_WEIGHT = 0.10
    POWER_PLAY_WEIGHT = 0.15
    RECENT_FORM_RATING_WEIGHT = 0.20
    SHOT_DIFF_WEIGHT = 0.05
    SOS_RATING_WEIGHT = 0.30


class goalie_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.30
    DISCIPLINE_WEIGHT = 0.05
    SAVE_PERCENTAGE_WEIGHT = 0.35
    GOALS_AGAINST_WEIGHT = 0.10
    SAVE_CONSISTENCY_WEIGHT = 0.20


class forward_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.33
    HITS_WEIGHT = 0.05
    DISIPLINE_WEIGHT = 0.05
    SHOT_BLOCKING_WEIGHT = 0.03
    PLUS_MINUS_WEIGHT = 0.02
    POINTS_WEIGHT = 0.25
    TAKEAWAYS_WEIGHT = 0.02
    CONTRIBUTION_WEIGHT = 0.15
    MULTIPOINT_WEIGHT = 0.10


class defensemen_rating_weights(Enum):
    UTILIZATION_WEIGHT = 0.33
    HITS_WEIGHT = 0.10
    DISIPLINE_WEIGHT = 0.07
    SHOT_BLOCKING_WEIGHT = 0.05
    PLUS_MINUS_WEIGHT = 0.03
    POINTS_WEIGHT = 0.20
    TAKEAWAYS_WEIGHT = 0.05
    CONTRIBUTION_WEIGHT = 0.10
    MULTIPOINT_WEIGHT = 0.07

team_weights = {
    'clutch_weight' : total_rating_weights.CLUTCH_RATING_WEIGHT.value,
    'goal_diff_weight' : total_rating_weights.GOAL_DIFF_WEIGHT.value,
    'penalty_kill_weight' : total_rating_weights.PENALTY_KILL_WEIGHT.value,
    'power_play_weight' : total_rating_weights.POWER_PLAY_WEIGHT.value,
    'recent_form_weight' : total_rating_weights.RECENT_FORM_RATING_WEIGHT.value,
    'shot_diff_weight' : total_rating_weights.SHOT_DIFF_WEIGHT.value,
    'strength_of_schedule_weight' : total_rating_weights.SOS_RATING_WEIGHT.value,
}

goalie_weights = {
    'utilization_weight' : goalie_rating_weights.UTILIZATION_WEIGHT.value,
    'discipline_weight' : goalie_rating_weights.DISCIPLINE_WEIGHT.value,
    'save_percentage_weight' :
        goalie_rating_weights.SAVE_PERCENTAGE_WEIGHT.value,
    'goals_against_weight' : goalie_rating_weights.GOALS_AGAINST_WEIGHT.value,
    'save_consitency_weight' :
        goalie_rating_weights.SAVE_CONSISTENCY_WEIGHT.value,
}

forward_weights = {
    'utilization_weight' : forward_rating_weights.UTILIZATION_WEIGHT.value,
    'hits_weight' : forward_rating_weights.HITS_WEIGHT.value,
    'discipline_weight' : forward_rating_weights.DISIPLINE_WEIGHT.value,
    'shot_blocking_weight' : forward_rating_weights.SHOT_BLOCKING_WEIGHT.value,
    'plus_minus_weight' : forward_rating_weights.PLUS_MINUS_WEIGHT.value,
    'points_weight' : forward_rating_weights.POINTS_WEIGHT.value,
    'takeaways_weight' : forward_rating_weights.TAKEAWAYS_WEIGHT.value,
    'contribution_weight' : forward_rating_weights.CONTRIBUTION_WEIGHT.value,
    'multipoint_weight' : forward_rating_weights.MULTIPOINT_WEIGHT.value,
}

defenseman_weights = {
    'utilization_weight' : defensemen_rating_weights.UTILIZATION_WEIGHT.value,
    'hits_weight' : defensemen_rating_weights.HITS_WEIGHT.value,
    'discipline_weight' : defensemen_rating_weights.DISIPLINE_WEIGHT.value,
    'shot_blocking_weight' :
        defensemen_rating_weights.SHOT_BLOCKING_WEIGHT.value,
    'plus_minus_weight' : defensemen_rating_weights.PLUS_MINUS_WEIGHT.value,
    'points_weight' : defensemen_rating_weights.POINTS_WEIGHT.value,
    'takeaways_weight' : defensemen_rating_weights.TAKEAWAYS_WEIGHT.value,
    'contribution_weight' : defensemen_rating_weights.CONTRIBUTION_WEIGHT.value,
    'multipoint_weight' : defensemen_rating_weights.MULTIPOINT_WEIGHT.value,
}


def update_team_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0 or len(weight_list) < 5:
        return
    team_weights['clutch_weight'] = weight_list[0]
    team_weights['defensive_weight'] = weight_list[1]
    team_weights['offensive_weight'] = weight_list[2]
    team_weights['recent_form_weight'] = weight_list[3]
    team_weights['strength_of_schedule_weight'] = weight_list[4]


def update_goalie_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0 or len(weight_list) < 5:
        return
    goalie_weights['utilization_weight'] = weight_list[0]
    goalie_weights['discipline_weight'] = weight_list[1]
    goalie_weights['save_percentage_weight'] = weight_list[2]
    goalie_weights['goals_against_weight'] = weight_list[3]
    goalie_weights['save_consitency_weight'] = weight_list[4]


def update_forward_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0 or len(weight_list) < 9:
        return
    forward_weights['utilization_weight'] = weight_list[0]
    forward_weights['hits_weight'] = weight_list[1]
    forward_weights['discipline_weight'] = weight_list[2]
    forward_weights['shot_blocking_weight'] = weight_list[3]
    forward_weights['plus_minus_weight'] = weight_list[4]
    forward_weights['points_weight'] = weight_list[5]
    forward_weights['takeaways_weight'] = weight_list[6]
    forward_weights['contribution_weight'] = weight_list[7]
    forward_weights['multipoint_weight'] = weight_list[8]


def update_defenseman_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0 or len(weight_list) < 9:
        return
    defenseman_weights['utilization_weight'] = weight_list[0]
    defenseman_weights['hits_weight'] = weight_list[1]
    defenseman_weights['discipline_weight'] = weight_list[2]
    defenseman_weights['shot_blocking_weight'] = weight_list[3]
    defenseman_weights['plus_minus_weight'] = weight_list[4]
    defenseman_weights['points_weight'] = weight_list[5]
    defenseman_weights['takeaways_weight'] = weight_list[6]
    defenseman_weights['contribution_weight'] = weight_list[7]
    defenseman_weights['multipoint_weight'] = weight_list[8]
