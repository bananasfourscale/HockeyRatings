from Ranking_Averages_Parser import *
from Matches_Parser import *
from Team_Summary_Parser import *
from asyncio.windows_events import NULL
import math

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


def determine_winner_loser(home_team : str = "", home_score : int = 0,
                           away_team : str = "", away_score : int = 0) \
                                                    -> tuple((str, str, int)):
        if home_score > away_score:
            return (home_team, away_team, home_score - away_score)
        else:
            return (away_team, home_team, away_score - home_score)


def get_latest_rankings(winning_team : str = "", losing_team : str = "",
                        game_date : datetime.date = None) \
                                                    -> tuple((float, float)):
    winner_rating = 0
    loser_rating = 0
    total_weeks = len(ranking_dates)-1
    try:
        
        # loop through all rating points until the most recent before the
        # date of the game is found
        while (total_weeks > 0):
            if game_date > ranking_dates[total_weeks]:
                winner_rating = float(
                    ranking_averages[winning_team][total_weeks])
                loser_rating = float(ranking_averages[losing_team][total_weeks])

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
        return (winner_rating, loser_rating)

    # a win by 3 goals is slightly closer and might have an ENG so slightly less
    if (score_difference == 3):
        return (winner_rating * 0.85, loser_rating * 0.85)

    # a win by 1/2 goals is generally a close game with an ENG likely majority
    # credit but not full
    if (score_difference >= 1 and extra_time == ""):
        return (winner_rating * 0.75, loser_rating * 0.75)

    # if you had to go to OT then it was a really close win
    if (extra_time == "OT"):
        return (winner_rating * 0.5, loser_rating * 0.5)

    # shootouts are basically just luck on some level and have little
    # correlation to how good the actual team is
    else:
        return (winner_rating * 0.33, loser_rating * 0.33)


def read_matches(match_list : list = []) -> None:

    # loop through the lines of file
    for game in match_list:
        date = game[match_indecies.DATE.value].split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
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
            date)

        # adjust the final points given/taken based on the size of the win
        (adjusted_winner_rating, adjusted_loser_rating) = scale_game_rating(
            winner_rating, loser_rating, score_difference, extra_time)

        # finally update the teams SOS rankings
        strength_of_schedule[winner] += (33 - adjusted_loser_rating)
        strength_of_schedule[loser] -= (adjusted_winner_rating)


def strength_of_schedule_scale_by_game() -> None:
    for team in strength_of_schedule.keys():
        strength_of_schedule[team] /= float(team_summary_data[team][
            summary_indecies.GP.value])

def strength_of_schedule_apply_sigmoid() -> None:
    for team in strength_of_schedule.keys():
        strength_of_schedule[team] = \
            1/(1 + math.exp(-(0.53466 * (strength_of_schedule[team]-5))))


if __name__ == "__main__":
    parse_average_ratings('Input_Files/AverageRatings.csv')
    parse_average_rating_header_row(average_ratings_header)
    parse_matches('Input_Files/Matches2021_2022.csv')
    parse_team_summary('Input_Files/TeamSummary.csv')
    read_matches(matches)
    strength_of_schedule_scale_by_game()
