import requests
import json
import math

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

last_ten_data = {
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

records_url = \
    'https://statsapi.web.nhl.com/api/v1/standings?expand=standings.record'

def parse_last_ten() -> None:
    web_data = requests.get(records_url)

    parsed_data = json.loads(web_data.content)
    for record in parsed_data["records"]:
        for team in record["teamRecords"]:
            last_10 = team["records"]["overallRecords"][3]

            # use the team name to sort the row data into the dictionary
            last_ten_data[team["team"]["name"]] = "{}-{}-{}".format(
                last_10["wins"], last_10["losses"], last_10["ot"])

def split_game_results(results : str = "") -> tuple((int, int)):
    game_result = results.split("-")
    return (game_result[0], game_result[2])


def form_calculate_rating() -> None:
    for team in last_ten_data.keys():
        (wins,  ot) = split_game_results(
            last_ten_data[team])
        recent_form_rating[team] = float(wins) + (float(ot) * 0.333)


def form_apply_sigmoid() -> None:
    for team in recent_form_rating.keys():
        recent_form_rating[team] = \
            1/(1 + math.exp(-(0.92 * (recent_form_rating[team] - 5))))


if __name__ == "__main__":
    parse_last_ten()
    form_calculate_rating()
    form_apply_sigmoid()
    for team in recent_form_rating.keys() :
        print("{}: {}".format(team, recent_form_rating[team]))
