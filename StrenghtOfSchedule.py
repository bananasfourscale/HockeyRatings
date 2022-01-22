
from asyncio.windows_events import NULL
import csv
import datetime
from turtle import home

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

ranking_averages = {
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
    'Montreal Canadiens' : [],
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

ranking_dates = [
    datetime.date(2021, 10, 16), # 0
    datetime.date(2021, 10, 23), # 1
    datetime.date(2021, 10, 30), # 2
    datetime.date(2021, 11, 6),  # 3
    datetime.date(2021, 11, 13), # 4
    NULL,                        # 5
    datetime.date(2021, 11, 20), # 6
    NULL,                        # 7
    datetime.date(2021, 11, 27), # 8
    datetime.date(2021, 12, 4),  # 9
    datetime.date(2021, 12, 11), # 10
    datetime.date(2022, 1, 1),   # 11
    NULL,                        # 12
    datetime.date(2022, 1, 2),   # 13
    datetime.date(2022, 1, 8),   # 14
    NULL,                        # 15
    datetime.date(2022, 1, 13),  # 16
]


def parse_average_ratings(file_name : str = "") -> None:
    with open(file_name, newline='') as csv_data_file:
        ratings = csv.reader(csv_data_file, delimiter = '\t')
        current_rating = 1

        # loop through the lines of file
        for rating in ratings:
            if current_rating == 1:
                ranking_averages['Anaheim Ducks'] = rating

            if current_rating == 2:
                ranking_averages['Arizona Coyotes'] = rating
                
            if current_rating == 3:
                ranking_averages['Boston Bruins'] = rating
                
            if current_rating == 4:
                ranking_averages['Buffalo Sabres'] = rating
                
            if current_rating == 5:
                ranking_averages['Calgary Flames'] = rating
                
            if current_rating == 6:
                ranking_averages['Carolina Hurricanes'] = rating
                
            if current_rating == 7:
                ranking_averages['Chicago Blackhawks'] = rating
                
            if current_rating == 8:
                ranking_averages['Colorado Avalanche'] = rating
                
            if current_rating == 9:
                ranking_averages['Columbus Blue Jackets'] = rating
                
            if current_rating == 10:
                ranking_averages['Dallas Stars'] = rating
                
            if current_rating == 11:
                ranking_averages['Detroit Red Wings'] = rating
                
            if current_rating == 12:
                ranking_averages['Edmonton Oilers'] = rating
                
            if current_rating == 13:
                ranking_averages['Florida Panthers'] = rating
                
            if current_rating == 14:
                ranking_averages['Los Angeles Kings'] = rating
                
            if current_rating == 15:
                ranking_averages['Minnesota Wild'] = rating
                
            if current_rating == 16:
                ranking_averages['Montreal Canadiens'] = rating
                
            if current_rating == 17:
                ranking_averages['Nashville Predators'] = rating
                
            if current_rating == 18:
                ranking_averages['New Jersey Devils'] = rating
                
            if current_rating == 19:
                ranking_averages['New York Islanders'] = rating
                
            if current_rating == 20:
                ranking_averages['New York Rangers'] = rating
                
            if current_rating == 21:
                ranking_averages['Ottawa Senators'] = rating
                
            if current_rating == 22:
                ranking_averages['Philadelphia Flyers'] = rating
                
            if current_rating == 23:
                ranking_averages['Pittsburgh Penguins'] = rating
                
            if current_rating == 24:
                ranking_averages['San Jose Sharks'] = rating
                
            if current_rating == 25:
                ranking_averages['Seattle Kraken'] = rating
                
            if current_rating == 26:
                ranking_averages['St. Louis Blues'] = rating
                
            if current_rating == 27:
                ranking_averages['Tampa Bay Lightning'] = rating
                
            if current_rating == 28:
                ranking_averages['Toronto Maple Leafs'] = rating
                
            if current_rating == 29:
                ranking_averages['Vancouver Canucks'] = rating
                
            if current_rating == 30:
                ranking_averages['Vegas Golden Knights'] = rating
                
            if current_rating == 31:
                ranking_averages['Washington Capitals'] = rating
                
            if current_rating == 32:
                ranking_averages['Winnipeg Jets'] = rating
            
            current_rating += 1
        #print(ranking_averages)


def determine_winner_loser(home_team : str = "", home_score : int = 0,
                           away_team : str = "", away_score : int = 0) \
                           -> tuple((str, str)):
        if home_score > away_score:
            return (home_team, away_team, home_score - away_score)
        else:
            return (away_team, home_team, away_score - home_score)


def update_strength_of_schedule(winning_team : str = "", losing_team : str = "",
                                game_date : datetime.date = None) -> None:
    winner_rating = 0
    loser_rating = 0

    total_weeks = len(ranking_dates)-1
    print(total_weeks)

    try:
        
        # loop through all rating points until the most recent before the date of the game is found
        while (total_weeks > 0):
            if (ranking_dates[total_weeks] is not NULL) and (game_date > ranking_dates[total_weeks]):
                winner_rating = float(ranking_averages[winning_team][total_weeks])
                loser_rating = float(ranking_averages[losing_team][total_weeks])
                break

            # if we havent found the most recent date, go back one more point
            total_weeks -= 1

        # if we didn't find the ranking point closest at all, there might not have been
        # any ranking data available at the time of the game. Just use a default which will
        # grant no points to either team.
        if total_weeks == 0:
            winner_rating = 0
            loser_rating = 33

        # adjust the ranking based on the score difference

        strength_of_schedule[winning_team] += (33 - loser_rating)
        strength_of_schedule[losing_team] -= (winner_rating)

    except Exception as e:
        print(winning_team, losing_team)
        raise e


def parse_matches(file_name : str = "") -> None:
    header_row = True
    with open(file_name, newline='') as csv_data_file:
        match_list = csv.reader(csv_data_file, delimiter = ',')

        # loop through the lines of file
        for game in match_list:
            if header_row :
                header_row = False
                continue

            date = game[0].split("-")
            date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            home_team = game[1]
            home_score = int(game[2])
            away_team = game[3]
            away_score = int(game[4])
            extra_time = game[5]

            # fill out a 3ple with the winner and loser of the game as well as
            # the scoring difference between the teams
            (winner, loser, score_difference) = \
                determine_winner_loser(home_team, home_score, away_team, away_score)

            # now given the winner, loser, and difference, update the SOS score.
            update_strength_of_schedule(winner, loser, date, score_difference)

        for team in strength_of_schedule.keys():
            print("{} : {}".format(team, strength_of_schedule[team]))


if __name__ == "__main__":
    parse_average_ratings('AverageRatings.csv')
    parse_matches('Matches2021_2022.csv')