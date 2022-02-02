from Team_Summary_Parser import *
from enum import *
import math

scoring_difference = {
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
    'Montreal Canadiens' : 0,
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

shooting_difference = {
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
    'Montreal Canadiens' : 0,
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

scoring_rating = {
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
    'Montreal Canadiens' : 0,
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


def scoring_rating_calc_goal_diff() -> None:
    for team in team_summary_data.keys():

        # reassign the data values just to make it easier to use
        games_played = team_summary_data[team][summary_indecies.GP.value]
        goals_for = team_summary_data[team][summary_indecies.GF.value]
        goals_against = team_summary_data[team][summary_indecies.GA.value]

        # calculate scoring diff
        scoring_difference[team] = \
            (float(goals_for) - float(goals_against)) / float(games_played)
        # print("{} : {}".format(team, scoring_difference[team]))


def scoring_rating_apply_sigmoid_goal_diff() -> None:
    for team in scoring_difference.keys():
        scoring_difference[team] = \
            1/(1 + math.exp(-(2.3 * (scoring_difference[team]))))
        # print("{} : {}".format(team, scoring_difference[team]))


def scoring_rating_calc_shooting_diff() -> None:
    for team in team_summary_data.keys():

        # reassign the data values just to make it easier to use
        games_played = team_summary_data[team][summary_indecies.GP.value]
        shots_for_per_game = team_summary_data[team][
            summary_indecies.SHF_GP.value]
        shots_against_per_game = team_summary_data[team][
            summary_indecies.SHA_GP.value]

        # calculate shooting diff
        shooting_difference[team] = \
            (float(shots_for_per_game) - float(shots_against_per_game))
        # print()
        # print("{} : SF/GP={}, SA/GP={}".format(team, shots_for_per_game,
        #     shots_against_per_game))
        # print("\t{}".format(shooting_difference[team]))


def scoring_rating_apply_sigmoid_shooting_diff() -> None:
    for team in shooting_difference.keys():
        shooting_difference[team] = \
            1/(1 + math.exp(-(0.46 * (shooting_difference[team]))))
        # print("{} : {}".format(team, shooting_difference[team]))

if __name__ == "__main__":
    parse_team_summary('Input_Files/TeamSummary.csv')
    pass