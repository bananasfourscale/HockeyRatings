import requests
import json
url1 = 'https://statsapi.web.nhl.com/api/v1/teams?expand=team.stats'

if __name__ == "__main__":
    records_url = \
        'https://statsapi.web.nhl.com/api/v1/standings?expand=standings.record'
    web_data = requests.get(records_url)
    last_ten_data = {}
    parsed_data = json.loads(web_data.content)
    for record in parsed_data["records"]:
        for team in record["teamRecords"]:
            with open("test_file.txt", 'w', encoding="utf-8") as file:
                file.write(str(team))
