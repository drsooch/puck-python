import json
import sys

import arrow
import click
import requests

from puck.urls import Url

GAME_A_STATUS = {
    'Preview': [1, 2],
    'Final': [6, 7],
    'Live': [3, 4]
}
GAME_D_STATUS = {
    'Preview': 1,
    'Pre-Game': 2,
    'Live': [3, 4],
    'Final': [6, 7]
}

_TEAM_ID_MAP = {
    'NJD': 1, 'NYI': 2, 'NYR': 3, 'PHI': 4,
    'PIT': 5, 'BOS': 6, 'BUF': 7, 'MTL': 8,
    'OTT': 9, 'TOR': 10, 'CAR': 12, 'FLA': 13,
    'TBL': 14, 'WSH': 15, 'CHI': 16, 'DET': 17,
    'NSH': 18, 'STL': 19, 'CGY': 20, 'COL': 21,
    'EDM': 22, 'VAN': 23, 'ANA': 24, 'DAL': 25,
    'LAK': 26, 'SJS': 28, 'CBJ': 29, 'MIN': 30,
    'WPG': 52, 'ARI': 53, 'VGK': 54
}

_TEAM_LN_MAP = {
    'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI', 'New York Rangers': 'NYR',
    'Philadelphia Flyers': 'PHI', 'Pittsburgh Penguins': 'PIT', 'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF', 'Montréal Canadiens': 'MTL', 'Ottawa Senators': 'OTT',
    'Toronto Maple Leafs': 'TOR', 'Carolina Hurricanes': 'CAR', 'Florida Panthers': 'FLA',
    'Tampa Bay Lightning': 'TBL', 'Washington Capitals': 'WSH', 'Chicago Blackhawks': 'CHI',
    'Detroit Red Wings': 'DET', 'Nashville Predators': 'NSH', 'St. Louis Blues': 'STL',
    'Calgary Flames': 'CGY', 'Colorado Avalanche': 'COL', 'Edmonton Oilers': 'EDM',
    'Vancouver Canucks': 'VAN', 'Anaheim Ducks': 'ANA', 'Dallas Stars': 'DAL',
    'Los Angeles Kings': 'LAK', 'San Jose Sharks': 'SJS', 'Columbus Blue Jackets': 'CBJ',
    'Minnesota Wild': 'MIN', 'Winnipeg Jets': 'WPG', 'Arizona Coyotes': 'ARI',
    'Vegas Golden Knights': 'VGK'
}


def get_url(url, url_mods=None, params=None):
    '''
    The base request for querying the NHL api. Attempts to get a JSON of
    requested information. In the event the request fails, a cached result will
    be checked. If this fails, a fatal error occurs and ends the program

    url should be a Url Enum

    TODO: Cache check? - currently have a cache function that does nothing
    TODO: Change the parameters to accept "appended" search terms - i.e. _SCHEDULE_URL + 'append'
    TODO: Better Error checking than '200 OK'
    '''

    if url_mods:
        url = _generate_url(url.value, url_mods)
    else:
        url = url.value

    with requests.get(url, params=params, timeout=5) as f:
        if f.status_code == requests.codes.ok:
            return f.json()
        else:
            cached_result = _get_from_cache(url, params)
            if cached_result:
                return json.load(cached_result)
            else:
                sys.exit('Fatal Error: Unable to load data, try again later.')


def _generate_url(url, url_mods):

    pass


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
