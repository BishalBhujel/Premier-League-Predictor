# import requests

# # url = 'https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season=2025&team=43'

# url ='https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season=2024&team=43&page=0&pageSize=100'

# data = requests.get(url)

# for data_in in data.json()['data']:
#     print(data_in['matchWeek'])

# https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season=2024&kickoff%3E2024-06-01&kickoff%3C2025-05-01&_limit=100&team=43


import requests

year = 2007
year_end = 2026
for year in range(year, year_end):
    url = f"https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season={year}&team=43&_limit=40"



    response = requests.get(
        url
    )

    data = response.json()

    for ind in data['data']:
        print(str(ind['kickoff'].strip('-')[0:4])+'     '+str(ind['matchWeek']))