import requests
import json

_SCHEDULE_URL = 'https://statsapi.web.nhl.com/api/v1/schedule'

_STATS_URL = 'https://statsapi.web.nhl.com/api/v1'

_RECORDS_URL = 'https://records.nhl.com/site/api'

_TEAMS = {
    "NJD": '1', "NYI": '2', "NYR": '3', "PHI": '4',
    "PIT": '5', "BOS": '6', "BUF": '7', "MTL": '8',
    "OTT": '9', "TOR": '10', "CAR": '12', "FLA": '13',
    "TBL": '14', "WSH": '15', "CHI": '16', "DET": '17',
    "NSH": '18', "STL": '19', "CGY": '20', "COL": '21',
    "EDM": '22', "VAN": '23', "ANA": '24', "DAL": '25',
    "LAK": '26', "SJS": '28', "CBJ": '29', "MIN": '30',
    "WPG": '52', "ARI": '53', "VGK": '54'
}

def _get_url(url, params=None):
    with requests.get(url, params) as f:
        return f.json()


