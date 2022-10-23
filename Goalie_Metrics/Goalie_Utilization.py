import requests
import json

if __name__ == "__main__":
    from Goalie_List import get_active_goalies, populate_active_goalies
else:
    from Goalie_Metrics.Goalie_List import get_active_goalies, \
        populate_active_goalies

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
            active_goalies[goalie])
        web_data = requests.get(goalie_url)
        parsed_data = json.loads(web_data.content)

        if len(parsed_data["stats"][0]["splits"]) > 0:
            time_on_ice = \
                parsed_data["stats"][0]["splits"][0]["stat"]["timeOnIce"]
            time_on_ice = time_on_ice.split(":")
            goalie_utilization_ranking[goalie] = \
                float(time_on_ice[0]) + (float(time_on_ice[1]) / 60)

if __name__ == "__main__":
    print("goalie utilization")
    populate_active_goalies()
    get_time_on_ice()
    print(goalie_utilization_ranking)