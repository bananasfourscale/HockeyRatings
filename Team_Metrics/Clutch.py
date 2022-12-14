import requests
import json

clutch_rating = {
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


def clutch_rating_get_dict() -> dict:
    return clutch_rating


def clutch_get_lead_data(match_data : dict={}) -> dict:
    
    # loop through the lines of file
    win_lead_first = {
        'Anaheim Ducks' : [0,0],
        'Arizona Coyotes' : [0,0],
        'Boston Bruins' : [0,0],
        'Buffalo Sabres' : [0,0],
        'Calgary Flames' : [0,0],
        'Carolina Hurricanes' : [0,0],
        'Chicago Blackhawks' : [0,0],
        'Colorado Avalanche' : [0,0],
        'Columbus Blue Jackets' : [0,0],
        'Dallas Stars' : [0,0],
        'Detroit Red Wings' : [0,0],
        'Edmonton Oilers' : [0,0],
        'Florida Panthers' : [0,0],
        'Los Angeles Kings' : [0,0],
        'Minnesota Wild' : [0,0],
        'Montréal Canadiens' : [0,0],
        'Nashville Predators' : [0,0],
        'New Jersey Devils' : [0,0],
        'New York Islanders' : [0,0],
        'New York Rangers' : [0,0],
        'Ottawa Senators' : [0,0],
        'Philadelphia Flyers' : [0,0],
        'Pittsburgh Penguins' : [0,0],
        'San Jose Sharks' : [0,0],
        'Seattle Kraken' : [0,0],
        'St. Louis Blues' : [0,0],
        'Tampa Bay Lightning' : [0,0],
        'Toronto Maple Leafs' : [0,0],
        'Vancouver Canucks' : [0,0],
        'Vegas Golden Knights' : [0,0],
        'Washington Capitals' : [0,0],
        'Winnipeg Jets' : [0,0],
    }
    win_lead_second = {
        'Anaheim Ducks' : [0,0],
        'Arizona Coyotes' : [0,0],
        'Boston Bruins' : [0,0],
        'Buffalo Sabres' : [0,0],
        'Calgary Flames' : [0,0],
        'Carolina Hurricanes' : [0,0],
        'Chicago Blackhawks' : [0,0],
        'Colorado Avalanche' : [0,0],
        'Columbus Blue Jackets' : [0,0],
        'Dallas Stars' : [0,0],
        'Detroit Red Wings' : [0,0],
        'Edmonton Oilers' : [0,0],
        'Florida Panthers' : [0,0],
        'Los Angeles Kings' : [0,0],
        'Minnesota Wild' : [0,0],
        'Montréal Canadiens' : [0,0],
        'Nashville Predators' : [0,0],
        'New Jersey Devils' : [0,0],
        'New York Islanders' : [0,0],
        'New York Rangers' : [0,0],
        'Ottawa Senators' : [0,0],
        'Philadelphia Flyers' : [0,0],
        'Pittsburgh Penguins' : [0,0],
        'San Jose Sharks' : [0,0],
        'Seattle Kraken' : [0,0],
        'St. Louis Blues' : [0,0],
        'Tampa Bay Lightning' : [0,0],
        'Toronto Maple Leafs' : [0,0],
        'Vancouver Canucks' : [0,0],
        'Vegas Golden Knights' : [0,0],
        'Washington Capitals' : [0,0],
        'Winnipeg Jets' : [0,0],
    }
    for date in match_data.keys():
        for game in match_data[date]:

            # away team data
            away_team = game["teams"]["away"]["team"]["name"]
            away_score_first = game["linescore"]["periods"][0]["away"]["goals"]
            away_score_second = \
                game["linescore"]["periods"][1]["away"]["goals"] + \
                away_score_first
            away_score_final = game["teams"]["away"]["score"]

            # home team data
            home_team = game["teams"]["home"]["team"]["name"]
            home_score_first = game["linescore"]["periods"][0]["home"]["goals"]
            home_score_second = \
                game["linescore"]["periods"][1]["home"]["goals"] + \
                home_score_first
            home_score_final = game["teams"]["home"]["score"]

            # determine who was leading after one period
            if away_score_first > home_score_first:
                if away_score_final > home_score_final:
                    win_lead_first[away_team][0] += 1
                    win_lead_first[away_team][1] += 1
                else:
                    win_lead_first[away_team][1] += 1
            else:
                if home_score_final > away_score_final:
                    win_lead_first[home_team][0] += 1
                    win_lead_first[home_team][1] += 1
                else:
                    win_lead_first[home_team][1] += 1
            
            # now do the same for the second period
            if away_score_second > home_score_second:
                if away_score_final > home_score_final:
                    win_lead_second[away_team][0] += 1
                    win_lead_second[away_team][1] += 1
                else:
                    win_lead_second[away_team][1] += 1
            else:
                if home_score_final > away_score_final:
                    win_lead_second[home_team][0] += 1
                    win_lead_second[home_team][1] += 1
                else:
                    win_lead_second[home_team][1] += 1


    # collect all the different permutations into one data set and return
    clutch_lead_data = {}
    for team in win_lead_first.keys():
        clutch_lead_data[team] = [win_lead_first[team], win_lead_second[team]]
    return clutch_lead_data


def clutch_calculate_lead_protection(match_data : dict={}) -> None:
    lead_protection_data = clutch_get_lead_data(match_data)
    for team in lead_protection_data.keys():

        # win protection first period
        if lead_protection_data[team][0][1] == 0:
            win_lead_first_per = 0.0
        else:
            win_lead_first_per = lead_protection_data[team][0][0] / \
                lead_protection_data[team][0][1]

        # lead protection second period
        if lead_protection_data[team][1][1] == 0:
            win_lead_second_per = 0.0
        else:
            win_lead_second_per = lead_protection_data[team][1][0] / \
                lead_protection_data[team][1][1]

        clutch_rating[team] += (win_lead_first_per) + (win_lead_second_per  * 2)
