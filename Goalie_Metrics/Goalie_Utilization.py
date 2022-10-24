import requests
import json

if __name__ == "__main__":
    from Goalie_List import get_active_goalies, populate_active_goalies, \
        get_team_IDs
else:
    from Goalie_Metrics.Goalie_List import get_active_goalies, \
        populate_active_goalies, get_team_IDs

goalie_utilization_ranking = {}

def get_goalie_utilization_ranking() -> dict:
    return goalie_utilization_ranking

def get_time_on_ice():

    # get the list of goalies
    active_goalies = get_active_goalies()

    # loop through and populate the time on ice
    for goalie in active_goalies.keys():
        goalie_url = "https://statsapi.web.nhl.com/api/v1/people/" + \
        "{}/stats?stats=statsSingleSeason&season=20222023".format(
            active_goalies[goalie][0])
        web_data = requests.get(goalie_url)
        parsed_data = json.loads(web_data.content)

        if len(parsed_data["stats"][0]["splits"]) > 0:
            records_url = \
                "https://statsapi.web.nhl.com/api/v1/teams/" + \
                "{}?expand=team.stats".format(
                    get_team_IDs()[active_goalies[goalie][1]])
            team_web_data = requests.get(records_url)
            team_parsed_data = json.loads(team_web_data.content)

            time_on_ice = \
                parsed_data["stats"][0]["splits"][0]["stat"]["timeOnIce"]
            time_on_ice = time_on_ice.split(":")
            goalie_utilization_ranking[goalie] = \
                (float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)) / \
                    team_parsed_data["teams"][0][
                        "teamStats"][0]["splits"][0]["stat"]["gamesPlayed"]

if __name__ == "__main__":
    print("goalie utilization")
    populate_active_goalies()
    get_time_on_ice()
    print(goalie_utilization_ranking)