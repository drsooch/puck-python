import asyncio
import json
import sys

import aiohttp
import arrow
import click
import requests

from .urls import Url, URLException


class TeamException(Exception):
    pass


GAME_STATUS = {
    'Preview': [1, 2, 8, 9],
    'Final': [5, 6, 7],
    'Live': [3, 4]
}
# GAME_D_STATUS = {
#     'Preview': 1,
#     'Pre-Game': 2,
#     'Live': [3, 4],
#     'Final': [6, 7]
# }

_TEAM_ID = {
    'NJD': 1, 'NYI': 2, 'NYR': 3, 'PHI': 4,
    'PIT': 5, 'BOS': 6, 'BUF': 7, 'MTL': 8,
    'OTT': 9, 'TOR': 10, 'CAR': 12, 'FLA': 13,
    'TBL': 14, 'WSH': 15, 'CHI': 16, 'DET': 17,
    'NSH': 18, 'STL': 19, 'CGY': 20, 'COL': 21,
    'EDM': 22, 'VAN': 23, 'ANA': 24, 'DAL': 25,
    'LAK': 26, 'SJS': 28, 'CBJ': 29, 'MIN': 30,
    'WPG': 52, 'ARI': 53, 'VGK': 54
}

_TEAM_SL = {
    'NJD': 'New Jersey Devils', 'NYI': 'New York Islanders',
    'NYR': 'New York Rangers', 'PHI': 'Philadelphia Flyers',
    'PIT': 'Pittsburgh Penguins', 'BOS': 'Boston Bruins',
    'BUF': 'Buffalo Sabres', 'MTL': 'Montréal Canadiens',
    'OTT': 'Ottawa Senators', 'TOR': 'Toronto Maple Leafs',
    'CAR': 'Carolina Hurricanes', 'FLA': 'Florida Panthers',
    'TBL': 'Tampa Bay Lightning', 'WSH': 'Washington Capitals',
    'CHI': 'Chicago Blackhawks', 'DET': 'Detroit Red Wings',
    'NSH': 'Nashville Predators', 'STL': 'St. Louis Blues',
    'CGY': 'Calgary Flames', 'COL': 'Colorado Avalanche',
    'EDM': 'Edmonton Oilers', 'VAN': 'Vancouver Canucks',
    'ANA': 'Anaheim Ducks', 'DAL': 'Dallas Stars',
    'LAK': 'Los Angeles Kings', 'SJS': 'San Jose Sharks',
    'CBJ': 'Columbus Blue Jackets', 'MIN': 'Minnesota Wild',
    'WPG': 'Winnipeg Jets', 'ARI': 'Arizona Coyotes',
    'VGK': 'Vegas Golden Knights'
}

_TEAM_LS = {
    'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI',
    'New York Rangers': 'NYR', 'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT', 'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF', 'Montréal Canadiens': 'MTL',
    'Ottawa Senators': 'OTT', 'Toronto Maple Leafs': 'TOR',
    'Carolina Hurricanes': 'CAR', 'Florida Panthers': 'FLA',
    'Tampa Bay Lightning': 'TBL', 'Washington Capitals': 'WSH',
    'Chicago Blackhawks': 'CHI', 'Detroit Red Wings': 'DET',
    'Nashville Predators': 'NSH', 'St. Louis Blues': 'STL',
    'Calgary Flames': 'CGY', 'Colorado Avalanche': 'COL',
    'Edmonton Oilers': 'EDM', 'Vancouver Canucks': 'VAN',
    'Anaheim Ducks': 'ANA', 'Dallas Stars': 'DAL',
    'Los Angeles Kings': 'LAK', 'San Jose Sharks': 'SJS',
    'Columbus Blue Jackets': 'CBJ', 'Minnesota Wild': 'MIN',
    'Winnipeg Jets': 'WPG', 'Arizona Coyotes': 'ARI',
    'Vegas Golden Knights': 'VGK'
}


def request(url, url_mods=None, params=None):
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
    TODO: Better Error checking than '200 OK'
    """

    if url_mods:
        _url = _generate_url(url, url_mods)
    else:
        _url = url.value
    try:
        with requests.get(_url, params=params, timeout=5) as f:
            if f.status_code == requests.codes.ok:
                return f.json()
            else:
                sys.exit('Fatal Error: Unable to load data, try again later.')
    except:
        # raise generic exception for a poor URL
        raise URLException


async def batch_request_create(game_ids, class_type):
    """Batch creation for Game objects. This drastically improves performance
        when creating multiple game objects.

    Args:
        game_ids (List of Ints): List of game ids to create game objects
        class_type (BaseGame): Game object type to create.
    Raises:
        URLException: NotImplemented

    Returns:
        [dict]: A list of game objects containing the json responses of
                each query.
    """
    async with aiohttp.ClientSession() as session:
        workers = []
        for _id in game_ids:
            workers.append(
                _create_game(Url.GAME, _id, class_type, session)
            )

        games = await asyncio.gather(*workers)
    return games


async def batch_request_update(games):
    async with aiohttp.ClientSession() as session:
        workers = []
        for game in games:
            workers.append(
                _update_game(Url.GAME, game, session)
            )

        await asyncio.gather(*workers)


async def _create_game(url, _id, class_type, session):
    url = _generate_url(url, {'game_id': _id})
    resp = await session.request(method='GET', url=url)
    json = await resp.json()

    if class_type == 'full':
        game = await _init_full(_id, json)
    elif class_type == 'banner':
        game = await _init_banner(_id, json)
    else:
        raise ValueError(f'{class_type} is not a valid game type.')

    return game


async def _update_game(url, game, session):
    url = _generate_url(url, {'game_id': game.game_id})
    resp = await session.request(method='GET', url=url)
    json = await resp.json()

    await _update_wrapper(game, json)


async def _init_full(_id, json):
    # This import is here to block a circular import
    # TODO: Restructure modules?
    from .Games import FullGame
    return FullGame(_id, json)


async def _init_banner(_id, json):
    from .Games import BannerGame
    return BannerGame(_id, json)


async def _update_wrapper(game, json):
    game.update(json)


def _generate_url(url, url_mods):
    """
    Takes a url and url modifications and creates a full Url
    Used to create a url with unique values (ie. Team, ID, etc.)
    """
    if Url.GAME == url:
        url = url.value.format(url_mods['game_id'])

    if Url.TEAMS == url:
        url = url.value.format(url_mods['team_id'])

    return url


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
        return _TEAM_ID[team]
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
        return _TEAM_LS[team]
    except KeyError as e:
        raise TeamException


def style(msg, format):
    format_type = {
        'error': {'fg': 'red'},
        'warning': {'fg': 'yellow'},
    }

    return click.style(msg, **format_type[format])
