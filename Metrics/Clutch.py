import requests
import json

clutch_rating = {
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


def clutch_rating_get_dict() -> dict:
    return clutch_rating


def clutch_lead_protection_get_data() -> dict:
    
    # Get the top level record from the API
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'
    web_data = requests.get(records_url)
    parsed_data = json.loads(web_data.content)

    # place the requried data into a dictionary for later use
    lead_protection_data = {}
    for team in parsed_data["teams"]:
        win_lead_first = team["teamStats"][0]["splits"][0]["stat"][
            "winLeadFirstPer"]
        win_lead_second = team["teamStats"][0]["splits"][0]["stat"][
            "winLeadSecondPer"]
        lead_protection_data[
            team["teamStats"][0]["splits"][0]["team"]["name"]] = \
                [win_lead_first, win_lead_second]
    return lead_protection_data

def clutch_calculate_lead_protection() -> None:
    lead_protection_data = clutch_lead_protection_get_data()
    for team in lead_protection_data.keys():

        # reassign the data values just to make it easier to use
        win_lead_1 = float(lead_protection_data[team][0])
        win_lead_2 = float(lead_protection_data[team][1])
        
        # calculate the positive clutch portion based on keeping leads
        clutch_rating[team] += (win_lead_1 * 5) + (win_lead_2 * 10)


if __name__ == "__main__":

    # localized import only for this file
    from Sigmoid_Correction import apply_sigmoid_correction

    # calculate the lead protection raw data
    clutch_calculate_lead_protection()
    print("Clutch Rating (Uncorrected):")
    for team in clutch_rating.keys():
        print("\t" + team + '=' + str(clutch_rating[team]))

    # now apply correction
    clutch_rating = apply_sigmoid_correction(clutch_rating_get_dict())
    print("Clutch Rating (Corrected):")
    for team in clutch_rating.keys():
        print("\t" + team + '=' + str(clutch_rating[team]))
