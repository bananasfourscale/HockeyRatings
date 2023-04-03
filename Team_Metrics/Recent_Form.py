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

streak_info = {
    'Anaheim Ducks' : ["W",0,0],
    'Arizona Coyotes' : ["W",0,0],
    'Boston Bruins' : ["W",0,0],
    'Buffalo Sabres' : ["W",0,0],
    'Calgary Flames' : ["W",0,0],
    'Carolina Hurricanes' : ["W",0,0],
    'Chicago Blackhawks' : ["W",0,0],
    'Colorado Avalanche' : ["W",0,0],
    'Columbus Blue Jackets' : ["W",0,0],
    'Dallas Stars' : ["W",0,0],
    'Detroit Red Wings' : ["W",0,0],
    'Edmonton Oilers' : ["W",0,0],
    'Florida Panthers' : ["W",0,0],
    'Los Angeles Kings' : ["W",0,0],
    'Minnesota Wild' : ["W",0,0],
    'Montréal Canadiens' : ["W",0,0],
    'Nashville Predators' : ["W",0,0],
    'New Jersey Devils' : ["W",0,0],
    'New York Islanders' : ["W",0,0],
    'New York Rangers' : ["W",0,0],
    'Ottawa Senators' : ["W",0,0],
    'Philadelphia Flyers' : ["W",0,0],
    'Pittsburgh Penguins' : ["W",0,0],
    'San Jose Sharks' : ["W",0,0],
    'Seattle Kraken' : ["W",0,0],
    'St. Louis Blues' : ["W",0,0],
    'Tampa Bay Lightning' : ["W",0,0],
    'Toronto Maple Leafs' : ["W",0,0],
    'Vancouver Canucks' : ["W",0,0],
    'Vegas Golden Knights' : ["W",0,0],
    'Washington Capitals' : ["W",0,0],
    'Winnipeg Jets' : ["W",0,0],
}

last_10_info = {
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

last_20_info = {
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

last_40_info = {
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
    LAST_10 = 0.25
    LAST_20 = 0.15
    LAST_40 = 0.10
    STREAK = 0.50


def recent_form_get_dict() -> dict:
    return recent_form_rating


def recent_form_get_streak_dict() -> dict:
    return streak_info


def recent_form_get_last_10_dict() -> dict:
    return last_10_info


def recent_form_get_last_20_dict() -> dict:
    return last_20_info


def recent_form_get_last_40_dict() -> dict:
    return last_40_info


def recent_form_get_trend_dict() -> dict:
    return recent_form_trends


def recent_form_get_data_set(match_data : dict={}) -> list:
    game_result = {}
    game_value = {}
    home_team = match_data['linescore']["teams"]["home"]["team"]["name"]
    home_score_final = match_data['linescore']["teams"]["home"]["score"]
    away_team = match_data['linescore']["teams"]["away"]["team"]["name"]
    away_score_final = match_data['linescore']["teams"]["away"]["score"]
    final_game_state = match_data['linescore']["linescore"][
        "currentPeriodOrdinal"]

    # determin the winner and loser from game score
    # determine who won and lost the game
    if home_score_final > away_score_final:
        winner = home_team
        loser = away_team
    else:
        winner = away_team
        loser = home_team

    # if the home team wins
    game_result[winner] = "W"
    game_value[winner] = 1.0
    if final_game_state == "3rd":
        game_result[loser] = "L"
        game_value[loser] = 0.0
    else:
        game_result[loser] = "OT"
        game_value[loser] = (0.33)
    return [game_result, game_value]


def recent_form_add_match_to_streak(streak : dict={}) -> None:
    for team in streak.keys():
        
        # if the streak is changed, update the number of different streaks
        # in the season
        if streak[team][0] != streak_info[team][0]:
            streak_info[team][2] += 1

        # now determine how to adjust the total streak score based on the
        # result type
        if streak[team][0] == "W":
            streak_info[team][1] += 1
        if streak[team][0] == "L":
            streak_info[team][1] -= 1
        else:
            streak_info[team][1] += (-1 / 3) 


def recent_form_add_match_to_recent_lists(match_score : dict={}) -> None:
    for team in match_score.keys():

        # if the last ten list is already full pop the first item off
        if len(last_10_info[team]) >= 10:
            last_10_info[team].pop(0)    
        last_10_info[team].append(match_score[team])

        # do the same but for the last twenty list
        if len(last_20_info[team]) >= 20:
            last_20_info[team].pop(0)
        last_20_info[team].append(match_score[team])

        # now finally do the same for last fourty
        if len(last_40_info[team]) >= 40:
            last_40_info[team].pop(0)
        last_40_info[team].append(match_score[team])


def recent_form_add_match_data(recent_form_data : dict={}) -> None:
    recent_form_add_match_to_streak(recent_form_data[0])
    recent_form_add_match_to_recent_lists(recent_form_data[1])


def recent_form_calculate_all() -> None:
    for team in recent_form_rating.keys():
        streak_info[team] = streak_info[team][1] / streak_info[team][2]
        last_10_info[team] = sum(last_10_info[team])
        last_20_info[team] = sum(last_20_info[team])
        last_40_info[team] = sum(last_40_info[team])


def recent_form_combine_metrics() -> None:
    for team in recent_form_rating.keys():
        recent_form_rating[team] = \
            (streak_info[team] * \
                recent_form_weights.STREAK.value) + \
            (last_10_info[team] * \
                recent_form_weights.LAST_10.value) + \
            (last_20_info[team] * \
                recent_form_weights.LAST_20.value) + \
            (last_40_info[team] * \
                recent_form_weights.LAST_40.value)


if __name__ == "__main__":

    # combine and scale wins + OT wins to get the rating form score for
    # the last ten games
    recent_form_metrics = recent_form_get_data_set()
    print("Recent Form (uncorrected):")
    for team in recent_form_rating.keys() :
        print("\t" + team + '=' + str(recent_form_rating[team]))
