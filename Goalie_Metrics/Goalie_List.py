import requests
import json

active_goalies = {}

team_codes = {
    'Anaheim Ducks' : 24,
    'Arizona Coyotes' : 53,
    'Boston Bruins' : 6,
    'Buffalo Sabres' : 7,
    'Calgary Flames' : 20,
    'Carolina Hurricanes' : 12,
    'Chicago Blackhawks' : 16,
    'Colorado Avalanche' : 21,
    'Columbus Blue Jackets' : 29,
    'Dallas Stars' : 25,
    'Detroit Red Wings' : 17,
    'Edmonton Oilers' : 22,
    'Florida Panthers' : 13,
    'Los Angeles Kings' : 26,
    'Minnesota Wild' : 30,
    'Montréal Canadiens' : 8,
    'Nashville Predators' : 18,
    'New Jersey Devils' : 1,
    'New York Islanders' : 2,
    'New York Rangers' : 3,
    'Ottawa Senators' : 9,
    'Philadelphia Flyers' : 4,
    'Pittsburgh Penguins' : 5,
    'San Jose Sharks' : 28,
    'Seattle Kraken' : 55,
    'St. Louis Blues' : 19,
    'Tampa Bay Lightning' : 14,
    'Toronto Maple Leafs' : 10,
    'Vancouver Canucks' : 23,
    'Vegas Golden Knights' : 54,
    'Washington Capitals' : 15,
    'Winnipeg Jets' : 52,
}


def get_active_goalies() -> dict:
    return active_goalies


def get_team_IDs() -> dict:
    return team_codes


def populate_active_goalies() -> None:

    if len(active_goalies.keys()) > 0:
        return

    # loop through each teams roster list
    for team in team_codes.keys():
        roster_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.roster".format(team_codes[team])
        web_data = requests.get(roster_url)
        parsed_data = json.loads(web_data.content)

        # for each player on the team loop
        for player in parsed_data["teams"][0]["roster"]["roster"]:

            # if the player is a Goalie, add them to the dict
            if player["position"]["name"] == "Goalie":
                active_goalies[player["person"]["fullName"]] = \
                    [player["person"]["id"], parsed_data["teams"][0]["name"]]
                

if __name__ == "__main__":
    populate_active_goalies()
    for player in active_goalies.keys():
        print("{}:{}".format(player, active_goalies[player]))
