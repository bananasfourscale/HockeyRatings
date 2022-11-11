import requests
import json


goalie_win_rating = {}


def goalie_win_rating_get_dict() -> dict:
    return goalie_win_rating


def goalie_win_rating_calculate(active_goalies : dict={}) -> None:

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():
        goalie_url = "https://statsapi.web.nhl.com/api/v1/people/" + \
        "{}/stats?stats=statsSingleSeason&season=20222023".format(
            active_goalies[goalie][0])
        web_data = requests.get(goalie_url)
        parsed_data = json.loads(web_data.content)

        # make sure the goalie has stats
        if len(parsed_data["stats"][0]["splits"]) > 0:
            player_data = parsed_data["stats"][0]["splits"][0]["stat"]

            # (W * 1) + (OTL * .33)
            wins = player_data["wins"]
            ot_losses = player_data["ot"]
            shutouts = player_data["shutouts"]
            goalie_win_rating[goalie] = (wins) + (ot_losses * 0.33) + \
                (shutouts * 0.1)


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
        'Goalie':{}
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
    goalie_win_rating_calculate(active_players['Goalie'])
    print("Goalie Utilization (uncorrected):")
    for goalie in goalie_win_rating.keys():
        print("\t" + goalie + '=' + str(goalie_win_rating[goalie]))
