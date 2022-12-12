import requests
import json


defensemen_hits_rating = {}


def defensemen_hits_get_dict() -> dict:
    return defensemen_hits_rating


def defensemen_hits_get_data(active_defensemens : dict={}) -> dict:

    # loop through and populate the time on ice
    for defensemen in active_defensemens.keys():

        # shortcut to access stats more cleanly
        player_stats = active_defensemens[defensemen][0]
        defensemen_hits_rating[defensemen] = player_stats["hits"]


if __name__ == "__main__":
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
    active_players = {
        'Center':{},
        'Right Wing':{},
        'Left Wing':{},
        'Defenseman':{},
        'defensemen':{}
    }

    # loop through each team
    for team in team_codes.keys():
        roster_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.roster".format(team_codes[team])
        web_data = requests.get(roster_url)
        parsed_data = json.loads(web_data.content)

        # for each listed player in the roster, store the name as the key
        # and the ID as the value so they can be individually searched later
        for player in parsed_data["teams"][0]["roster"]["roster"]:
            active_players[player["position"]["name"]] \
                [player["person"]["fullName"]] = \
                    [player["person"]["id"], parsed_data["teams"][0]["name"]]

    sp_metrics = defensemen_hits_get_data(active_players['defensemen'])
    for defensemen in defensemen_hits_rating.keys():
        print("\t" + defensemen + '=' + str(defensemen_hits_rating[defensemen]))
