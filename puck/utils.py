import requests
import json
import sys
import click

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
    '''
    The base request for querying the NHL api. Attempts to get a JSON of
    requested information. In the event the request fails, a cached result will
    be checked. If this fails, a fatal error occurs and ends the program

    TODO: cleaning response data -> will cached result be cleaned or full response?
    '''
    with requests.get(url, params=params, timeout=5) as f:
        if f.status_code == requests.codes.ok:
            return f.json()
        else:
            cached_result = _get_from_cache(url, params)
            if cached_result:
                return json.load(cached_result)
            else:
                sys.exit('Fatal Error: Unable to load data, try again later.')


def _get_from_cache(url, params):
    '''
    Check to see if requested information is in the cache and hasn't gone stale

    TODO: Dealing with cached results that don't match params
    '''
    return None


def style(msg, format):
    format_type = {
        'error': {'fg': 'red'},
        'warning': {'fg': 'yellow'}
    }

    return click.style(msg, **format_type[format])
