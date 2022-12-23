from enum import Enum
import requests
import json
import datetime

strength_of_schedule = {
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

class strength_of_schedule_weights(Enum):
    WIN_REGULATION_WEIGHT = 1.0
    WIN_OT_WEIGHT = 0.33
    LOSE_OT_WEIGHT = 0.10
    WIN_SO_WEIGHT = 0.10
    LOSE_SO_WEIGHT = 0.05


class match_indecies(Enum):
    AWAY_TEAM = 0
    AWAY_SCORE = 1
    HOME_TEAM = 2
    HOME_SCORE = 3
    EXTRA_TIME = 4


def strength_of_schedule_get_dict() -> dict:
    return strength_of_schedule


def determine_winner_loser(home_team : str = "", home_score : int = 0,
    away_team : str = "", away_score : int = 0) -> tuple((str, str, int)):

    # simple case to determine which team won the game
    if home_score > away_score:
        return (home_team, away_team, home_score - away_score)
    else:
        return (away_team, home_team, away_score - home_score)


def get_latest_rankings(winning_team : str = "", losing_team : str = "",
    game_date : datetime.date = None, average_rankings : dict = {},
    ranking_dates : list = []) -> tuple((float, float)):

    # loop through the total number of ranking weeks until gettin the latest
    total_weeks = len(list(average_rankings.values())[0])-1
    try:
        
        # loop through all rating points until the most recent before the
        # date of the game is found
        while (total_weeks >= 0):
            if game_date >= ranking_dates[total_weeks]:
                loser_rating = float(average_rankings[losing_team][total_weeks])
                winner_rating = \
                    float(average_rankings[winning_team][total_weeks])

                # if we find the correct week, then skip the loop
                break

            # if we havent found the most recent date, go back one more point
            total_weeks -= 1

        # if we didn't find the ranking point closest at all,
        # there might not have been any ranking data available at the time
        # of the game. Just use a default which will grant no points
        # to either team.
        if total_weeks < 0:
            loser_rating = 32
            winner_rating = 1
        return (loser_rating, winner_rating)
    except Exception as e:
        print(winning_team, losing_team)
        print("error index: {}".format(total_weeks))
        raise e


def scale_game_rating(loser_rating : float=0.0, winner_rating : float=0.0,
    score_difference : int=1, extra_time : str="") -> float:

    # regulation wins give full points to the winner
    if (extra_time == "3rd"):
        return (
            (loser_rating *
                strength_of_schedule_weights.WIN_REGULATION_WEIGHT.value),
            0.0
        )

    # if you had to go to OT then it was a really close win
    if (extra_time == "OT"):
        return (
            (loser_rating * strength_of_schedule_weights.WIN_OT_WEIGHT.value),
            (winner_rating * strength_of_schedule_weights.LOSE_OT_WEIGHT.value)
        )

    # shoot outs give basically no credit to either team because they suck
    return (
        (loser_rating * strength_of_schedule_weights.WIN_SO_WEIGHT.value),
        (winner_rating * strength_of_schedule_weights.LOSE_SO_WEIGHT.value)
    )


def read_matches(average_rankings : dict={}, ranking_dates : list=[],
                 match_data : dict={}) -> None:

    # loop through the lines of file
    for date in match_data.keys():
        for game in match_data[date]:
            date_str = date.split("-")
            game_date = datetime.date(int(date_str[0]), int(date_str[1]),
                int(date_str[2]))
            away_team = game["teams"]["away"]["team"]["name"]
            away_score = game["teams"]["away"]["score"]
            home_team = game["teams"]["home"]["team"]["name"]
            home_score = game["teams"]["home"]["score"]
            extra_time = game["linescore"]["currentPeriodOrdinal"]

            # fill out a 3ple with the winner and loser of the game as well as
            # the scoring difference between the teams
            (winner, loser, score_difference) = determine_winner_loser(
                home_team, home_score, away_team, away_score)

            # now given the winner, loser, get the latest rankings for the two
            # teams that they should use for the update
            (loser_rating, winner_rating) = \
                get_latest_rankings(winner, loser, game_date, average_rankings,
                    ranking_dates)

            # adjust the final points given/taken based on the size of the win
            (adjusted_loser_rating, adjusted_winner_rating) = \
                scale_game_rating((33 - loser_rating), (33 - winner_rating),\
                    score_difference, extra_time)
            strength_of_schedule[winner] += adjusted_loser_rating
            strength_of_schedule[loser] += adjusted_winner_rating


def strength_of_schedule_scale_by_game(team_stats : dict={}) -> None:

    # place the requried data into a dictionary for later use
    for team in team_stats.keys():
        strength_of_schedule[team] /= \
            float(team_stats[team]["gamesPlayed"])


def strength_of_schedule_calculate(average_rankings : dict={},
                                   ranking_dates : list=[],
                                   match_data : dict={}) -> None:

    # first call read matches which will generate the absolute score for all
    # teams by parsing all complete games one-by-one
    read_matches(average_rankings, ranking_dates, match_data)
