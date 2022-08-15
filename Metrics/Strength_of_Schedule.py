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
    FOUR_OR_MORE = 1.0
    THREE_GOALS = 0.85
    TWO_OR_ONE = 0.75
    OT_GAME = 0.5
    SO_GAME = 0.10


class match_indecies(Enum):
    AWAY_TEAM = 0
    AWAY_SCORE = 1
    HOME_TEAM = 2
    HOME_SCORE = 3
    EXTRA_TIME = 4


def strength_of_schedule_get_dict() -> dict:
    return strength_of_schedule


def strength_of_schedule_get_match_data() -> dict:
    # Get the top level record from the API
    records_url = \
        "https://statsapi.web.nhl.com/api/v1/schedule?season=20212022" + \
            "&gameType=R&expand=schedule.linescore"
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    # place match data in a dict of list of games for later use
    match_data = {}
    # matches are orginized by date they take place
    for date in parsed_data["dates"]:
        game_data = []

        # for each game on a specific date loop through
        for game in date["games"]:

            # if the game is a completed regular season game then add to list
            if (game["status"]["abstractGameState"] == "Final"):
                away_name = game["teams"]["away"]["team"]["name"]
                away_score = game["teams"]["away"]["score"]
                home_name = game["teams"]["home"]["team"]["name"]
                home_score = game["teams"]["home"]["score"]
                game_end_type = game["linescore"]["currentPeriodOrdinal"]
                game_data.append([away_name, away_score, home_name, home_score,
                    game_end_type])
        match_data[date["date"]] = game_data
    return match_data

def determine_winner_loser(home_team : str = "", home_score : int = 0,
                           away_team : str = "", away_score : int = 0) \
                                                    -> tuple((str, str, int)):
        if home_score > away_score:
            return (home_team, away_team, home_score - away_score)
        else:
            return (away_team, home_team, away_score - home_score)


def get_latest_rankings(winning_team : str = "", losing_team : str = "",
                        game_date : datetime.date = None,
                        average_rankings : dict = {}, ranking_dates : list = [])\
                                                     -> tuple((float, float)):

    winner_rating = 0
    loser_rating = 0
    total_weeks = len(list(average_rankings.values())[0])-1
    try:
        
        # loop through all rating points until the most recent before the
        # date of the game is found
        while (total_weeks > 0):
            if game_date > ranking_dates[total_weeks]:
                winner_rating = float(
                    average_rankings[winning_team][total_weeks])
                loser_rating = float(average_rankings[losing_team][total_weeks])

                # if we find the correct week, then skip the loop
                break

            # if we havent found the most recent date, go back one more point
            total_weeks -= 1

        # if we didn't find the ranking point closest at all,
        # there might not have been any ranking data available at the time
        # of the game. Just use a default which will grant no points
        # to either team.
        if total_weeks == 0:
            winner_rating = 0
            loser_rating = 33

        return (winner_rating, loser_rating)

    except Exception as e:
        print(winning_team, losing_team)
        print("error index: {}".format(total_weeks))
        raise e


def scale_game_rating(winner_rating : float = 0.0, loser_rating : float = 0.0,
                      score_difference : int = 1, extra_time : str = "") \
                                                    -> tuple((float, float)):

    # any win by 4 or more goals gets full credit
    if (score_difference >= 4):
        return (winner_rating * strength_of_schedule_weights.FOUR_OR_MORE.value,
            loser_rating * strength_of_schedule_weights.FOUR_OR_MORE.value)

    # a win by 3 goals is slightly closer and might have an ENG so slightly less
    if (score_difference == 3):
        return (winner_rating * strength_of_schedule_weights.THREE_GOALS.value,
            loser_rating * strength_of_schedule_weights.THREE_GOALS.value)

    # a win by 1/2 goals is generally a close game with an ENG likely majority
    # credit but not full
    if ((score_difference >= 1) and (extra_time == "3rd")):
        return (winner_rating * strength_of_schedule_weights.TWO_OR_ONE.value,
            loser_rating * strength_of_schedule_weights.TWO_OR_ONE.value)

    # if you had to go to OT then it was a really close win
    if (extra_time == "OT"):
        return (winner_rating * strength_of_schedule_weights.OT_GAME.value,
            loser_rating * strength_of_schedule_weights.OT_GAME.value)

    # shootouts are basically just luck on some level and have little
    # correlation to how good the actual team is
    else:
        return (winner_rating * strength_of_schedule_weights.SO_GAME.value,
            loser_rating * strength_of_schedule_weights.SO_GAME.value)


def read_matches(average_rankings : dict = {}, ranking_dates : list = []) \
                                                                        -> None:
    match_data = strength_of_schedule_get_match_data()

    # loop through the lines of file
    for date in match_data.keys():
        for game in match_data[date]:
            date_str = date.split("-")
            game_date = datetime.date(int(date_str[0]), int(date_str[1]),
                int(date_str[2]))
            away_team = game[match_indecies.AWAY_TEAM.value]
            away_score = int(game[match_indecies.AWAY_SCORE.value])
            home_team = game[match_indecies.HOME_TEAM.value]
            home_score = int(game[match_indecies.HOME_SCORE.value])
            extra_time = game[match_indecies.EXTRA_TIME.value]

            # fill out a 3ple with the winner and loser of the game as well as
            # the scoring difference between the teams
            (winner, loser, score_difference) = determine_winner_loser(
                home_team, home_score, away_team, away_score)

            # now given the winner, loser, get the latest rankings for the two
            # teams that they should use for the update
            (winner_rating, loser_rating) = get_latest_rankings(winner, loser,
                game_date, average_rankings, ranking_dates)

            # adjust the final points given/taken based on the size of the win
            (adjusted_winner_rating, adjusted_loser_rating) = scale_game_rating(
                winner_rating, loser_rating, score_difference, extra_time)

            # finally update the teams SOS rankings
            strength_of_schedule[winner] += (33 - adjusted_loser_rating)
            strength_of_schedule[loser] -= (adjusted_winner_rating)


def strength_of_schedule_scale_by_game() -> None:

     # Get the top level record from the API
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    # place the requried data into a dictionary for later use
    for team in parsed_data["teams"]:
        strength_of_schedule[
            team["teamStats"][0]["splits"][0]["team"]["name"]] /= \
            float(team["teamStats"][0]["splits"][0]["stat"]["gamesPlayed"])


def strength_of_schedule_calculate(average_rankings : dict = {},
                                   ranking_dates : list = []) -> None:

    # first call read matches which will generate the absolute score for all
    # teams by parsing all complete games one-by-one
    read_matches(average_rankings, ranking_dates)

    # then scale each teams score by how many games they specifically have
    # played
    strength_of_schedule_scale_by_game()


if __name__ == "__main__":

    # localized import only for this file
    from Sigmoid_Correction import apply_sigmoid_correction
    from Average_Ranking_Parser import average_rankings_parse, \
        average_rankings_get_dict, average_ranking_get_ranking_dates

    # parse the average ranking file to get matchup scores
    average_rankings_parse('Output_Files/Trend_Files/AverageRankings.csv')

    # calculate the uncorrected strength of schedule
    strength_of_schedule_calculate(average_rankings_get_dict())
    print("Strength of Schedule (Uncorrected):")
    for team in strength_of_schedule.keys():
        print("\t" + team + '=' + str(strength_of_schedule[team]))
    
    # now apply adaptive sigmoid
    strength_of_schedule = apply_sigmoid_correction(
        strength_of_schedule_get_dict())
    print("Strength of Schedule (Corrected):")
    for team in strength_of_schedule.keys():
        print("\t" + team + '=' + str(strength_of_schedule[team]))
