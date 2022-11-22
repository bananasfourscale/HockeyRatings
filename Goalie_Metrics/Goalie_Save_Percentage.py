import requests
import json


goalie_save_percentage_rating = {}


def goalie_save_percentage_get_dict() -> dict:
    return goalie_save_percentage_rating


def goalie_save_percentage_get_data(active_goalies : dict={}) -> list:
    even_strength_sp = {}
    power_play_sp = {}
    penalty_kill_sp = {}

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():
        goalie_url = "https://statsapi.web.nhl.com/api/v1/people/" + \
        "{}/stats?stats=statsSingleSeason&season=20222023".format(
            active_goalies[goalie][0])
        web_data = requests.get(goalie_url)
        parsed_data = json.loads(web_data.content)

        # make sure the goalie has stats
        if len(parsed_data["stats"][0]["splits"]) > 0:

            # shortcut to access stats more cleanly
            player_stats = parsed_data["stats"][0]["splits"][0]["stat"]

            # get even strength data
            even_strength_sp[goalie] = \
                player_stats["evenStrengthSavePercentage"]

            # get powerplay data if it exist (own team short handed)
            if player_stats["powerPlayShots"] > 0:
                power_play_sp[goalie] = \
                    player_stats["powerPlaySavePercentage"]
            else:
                power_play_sp[goalie] = 100.0

            # get short handed data if it exist (own team power play)
            if player_stats["shortHandedShots"] > 0:
                penalty_kill_sp[goalie] = \
                    player_stats["shortHandedSavePercentage"]
            else:
                penalty_kill_sp[goalie] = 100.0
    return [even_strength_sp, power_play_sp, penalty_kill_sp]


def goalie_save_percentage_scale_for_volume(metric_list : list=[],
    active_goalies : dict={}) -> list:
    for goalie in metric_list[0].keys():
        goalie_url = "https://statsapi.web.nhl.com/api/v1/people/" + \
        "{}/stats?stats=statsSingleSeason&season=20222023".format(
            active_goalies[goalie][0])
        web_data = requests.get(goalie_url)
        parsed_data = json.loads(web_data.content)

        # make sure the goalie has stats
        if len(parsed_data["stats"][0]["splits"]) > 0:

            # shortcut to access stats more cleanly
            player_stats = parsed_data["stats"][0]["splits"][0]["stat"]

            # (S%_ev / 100) * S_ev
            # (S%_pp / 100) * S_pp
            # (S%_sh / 100) * S_sh
            metric_list[0][goalie] = (metric_list[0][goalie] / 100) * \
                player_stats['evenSaves']
            metric_list[1][goalie] = (metric_list[1][goalie] / 100) * \
                player_stats['powerPlaySaves']
            metric_list[2][goalie] = (metric_list[2][goalie] / 100) * \
                player_stats['shortHandedSaves']

    return metric_list



def goalie_save_percentage_combine_metrics(metric_list : list=[],
    active_goalies : dict={}, team_IDs : dict={}) -> None:
    
    # unlike other stats which use a flat weight. Have this weight scale so that
    # roughly the percentage of time at each strength is the percent weight.
    # This is designed to be applied after some other corrections but can be
    # applied proactively as well
    for goalie in metric_list[0].keys():
        team_url = \
            "https://statsapi.web.nhl.com/api/v1/teams/" + \
            "{}?expand=team.stats".format(
                team_IDs[active_goalies[goalie][1]])
        team_web_data = requests.get(team_url)
        team_parsed_data = json.loads(team_web_data.content)
        team_stats = team_parsed_data["teams"][0]["teamStats"][0]["splits"][
            0]["stat"]

        # get roughly the total ice time for the team of this goalie
        games_played = team_stats["gamesPlayed"]
        total_ice_time = games_played * 60

        # now calculate the percentage of time on the power play, meaning all
        # saves are short handed. Use this as short handed weight
        pp_time = team_stats["powerPlayOpportunities"] * 2
        short_handed_sp_weight = pp_time / total_ice_time

        # now with less available stats in the api do a more roundabout way to
        # get the time on the penalty kill which will become the pp weight
        sh_chances = round(team_stats["powerPlayGoalsAgainst"] / \
            team_stats["powerPlayGoalsAgainst"])
        sh_time = sh_chances * 2
        power_play_sp_weight = sh_time / total_ice_time

        # now the even strength must just be the remainder
        even_strength_sp_weight = (total_ice_time - (sh_time + pp_time)) / \
            total_ice_time
        
        goalie_save_percentage_rating[goalie] = \
            (metric_list[0][goalie] * even_strength_sp_weight) + \
            (metric_list[1][goalie] * power_play_sp_weight) + \
            (metric_list[2][goalie] * short_handed_sp_weight)


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

    sp_metrics = goalie_save_percentage_get_data(active_players['Goalie'])

    # TODO this does nothing but get data and throw it away, look at team
    # offenseive and defensive ratings to get an idea of how to do it
    goalie_save_percentage_combine_metrics(sp_metrics,
        active_players['Goalie'], team_codes)
    for goalie in goalie_save_percentage_rating.keys():
        print("\t" + goalie + '=' + str(goalie_save_percentage_rating[goalie]))
