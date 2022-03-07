from Parsers.Team_Summary_Parser import *
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

class win_rating_weights(Enum):
    REG_WIN = 100.0
    OT_WIN = 66.666
    OT_LOSSES = 33.333
    SHOOTOUT_WIN = 10.0

def win_rating_calc() -> None:
    for team in team_summary_data.keys():

        # reassign the data values just to make it easier to use
        games_played = float(team_summary_data[team][summary_indecies.GP.value])
        regulation_wins = float(
            team_summary_data[team][summary_indecies.RW.value])
        reg_plus_ot_wins = float(
            team_summary_data[team][summary_indecies.ROW.value])
        shootout_wins = float(
            team_summary_data[team][summary_indecies.SOW.value])
        ot_losses = float(team_summary_data[team][summary_indecies.OT.value])

        # apply all weights based on the type of win/loss
        win_rating[team] = regulation_wins * win_rating_weights.REG_WIN.value
        win_rating[team] += (reg_plus_ot_wins - regulation_wins) * \
            win_rating_weights.OT_WIN.value
        win_rating[team] += ot_losses * win_rating_weights.OT_LOSSES.value
        win_rating[team] += shootout_wins * \
            win_rating_weights.SHOOTOUT_WIN.value
        win_rating[team] /= games_played
        win_rating[team] /= 100.0
    return


if __name__ == "__main__":
    parse_team_summary('Input_Files/TeamSummary.csv')
    win_rating_calc()
    print(win_rating)