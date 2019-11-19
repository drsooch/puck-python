import json

import arrow
import click
import requests

from puck.urls import Url
import sys


class TeamException(Exception):
    pass


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
    """
    The base request for querying the NHL api. Attempts to get a JSON of
    requested information. In the event the request fails, a cached result will
    be checked. If this fails, a fatal error occurs and ends the program

    Args:
        url (Url): The url to query (from puck.Url)

    Kwargs:
        url_mods (dict): Any modifications for the base Url
        params (dict): Any parameters to pass to the Url

    Returns:
        json

    TODO: Cache check? - currently have a cache function that does nothing
    TODO: Change the parameters to accept "appended" search terms - i.e. _SCHEDULE_URL + 'append'
    TODO: Better Error checking than '200 OK'
    """

    if url_mods:
        _url = _generate_url(url.value, url_mods)
    else:
        _url = url.value

    with requests.get(_url, params=params, timeout=5) as f:
        if f.status_code == requests.codes.ok:
            return f.json()
        else:
            cached_result = _get_from_cache(_url, params)
            if cached_result:
                return json.load(cached_result)
            else:
                sys.exit('Fatal Error: Unable to load data, try again later.')


def _generate_url(url, url_mods):
    if Url.GAME.value == url:
        url = url.format(url_mods['game_id'])

    return url


def _get_from_cache(url, params):
    """
    Check to see if requested information is in the cache and hasn't gone stale

    TODO: Dealing with cached results that don't match params
    """
    return None


def team_to_id(team):
    """
    Return a teams ID number. Accepts both Long Name and Abbreviation.

    Args:
        team (str): Either Long Name or Abbreviation

    Returns:
        int: ID number

    Raises:
        TeamException
    """

    # means its probably in long form
    if len(team) != 3:
        try:
            team = shorten_tname(team)
        except TeamException as e:
            # Do I even need this or will it propogate?
            raise TeamException

    try:
        return _TEAM_ID_MAP[team]
    except KeyError as e:
        raise TeamException


def shorten_tname(team):
    """
    Returns 3-Letter Team Abbreviation.

    Args:
        team (str): Full Team Name

    Returns:
        str: 3-Letter Team Abb.

    Raises:
        TeamException
    """
    try:
        return _TEAM_LN_MAP[team]
    except KeyError as e:
        raise TeamException


def style(msg, format):
    format_type = {
        'error': {'fg': 'red'},
        'warning': {'fg': 'yellow'},
        'winner': {'fg': 'green'},
        'general': {'fg': 'white'},
        'title': {'fg': 'white', 'underline': True}
    }

    return click.style(msg, **format_type[format])
