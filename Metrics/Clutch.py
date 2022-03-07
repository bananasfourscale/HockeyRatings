from Parsers.Leading_Trailing_Parser import *
import math

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


def clutch_calculate_lead_protection() -> None:
    for team in leading_trailing_data.keys():

        # reassign the data values just to make it easier to use
        win_lead_1 = float(
            leading_trailing_data[team][
                leading_trailing_indecies.W_PER_LEAD_1.value])
        win_lead_2 = float(
            leading_trailing_data[team][
                leading_trailing_indecies.W_PER_LEAD_2.value])
        
        # calculate the positive clutch portion based on keeping leads
        clutch_rating[team] = (win_lead_1 * 5) + (win_lead_2 * 10)
        # print("{} : {}".format(team, clutch_rating[team]))


def clutch_calculated_trail_comeback() -> None:
    for team in leading_trailing_data.keys():

        # reassign the data values just to make it easier to use
        win_trail_1 = float(
            leading_trailing_data[team][
                leading_trailing_indecies.W_PER_TRAIL_1.value])
        win_trail_2 = float(
            leading_trailing_data[team][
                leading_trailing_indecies.W_PER_TRAIL_2.value])

        # calculate the negative clutch portion baed on failing to come back
        clutch_rating[team] += ((1-win_trail_1) * -5) + ((1-win_trail_2) * -10)
        # print("{} : {}".format(team, clutch_rating[team]))


def clutch_apply_sigmoid() -> None:
    for team in clutch_rating.keys():
        clutch_rating[team] = \
            1/(1 + math.exp(-(0.306667 * (clutch_rating[team]))))


if __name__ == "__main__":
    parse_leading_trailing("Input_Files/LeadingTrailing.csv")
    clutch_calculate_lead_protection()
    clutch_calculated_trail_comeback()
    clutch_apply_sigmoid()
