import requests
import json
from math import exp

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


def recent_form_get_data() -> dict:
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/standings?expand=standings.record'
    web_data = requests.get(records_url)
    last_ten_data = {}
    parsed_data = json.loads(web_data.content)
    for record in parsed_data["records"]:
        for team in record["teamRecords"]:
            last_10 = team["records"]["overallRecords"][3]

            # use the team name to sort the row data into the dictionary
            last_ten_data[team["team"]["name"]] = "{}-{}-{}".format(
                last_10["wins"], last_10["losses"], last_10["ot"])
    return last_ten_data


def recent_form_split_game_results(results : str = "") -> tuple((int, int)):
    game_result = results.split("-")
    return (game_result[0], game_result[2])


def recent_form_calculate_rating() -> None:
    last_ten_data = recent_form_get_data()
    for team in last_ten_data.keys():
        (wins,  ot) = recent_form_split_game_results(
            last_ten_data[team])
        recent_form_rating[team] = float(wins) + (float(ot) * 0.333)


def recent_form_apply_sigmoid() -> None:
    for team in recent_form_rating.keys():
        recent_form_rating[team] = \
            1/(1 + exp(-(0.92 * (recent_form_rating[team] - 5))))


if __name__ == "__main__":
    recent_form_calculate_rating()
    recent_form_apply_sigmoid()
    print("Recent Form:")
    for team in recent_form_rating.keys() :
        print("\t" + team + '=' + str(recent_form_rating[team]))
