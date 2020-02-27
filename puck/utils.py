import asyncio
import json
import sys

import aiohttp
import arrow
import click
import requests

import puck.parser as parser
from puck.dispatcher import Dispatch

from .urls import Url, URLException


class TeamException(Exception):
    pass


class ConfigError(Exception):
    pass


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
                print(f'HTTP Error: {f.status_code} on -> {_url}')
                sys.exit('Fatal Error: Unable to load data, try again later.')
    except Exception as e:
        print(e)


async def async_request(url, session, url_mods=None, params=None) -> dict:  # noqa
    """Base async request for polling one endpoint.

    Args:
        url (Url): Url to query
        session (ClientSession): AIOHTTP ClientSession Object
        url_mods (dict): modifications to the Url passed
        params (dict): url parameters for the Url passed

    Kwargs:
        kwargs to be passed to the function supplied

    Returns:
        dict or None: dict object representing a JSON response
    """
    if url_mods:
        url = _generate_url(url, url_mods)
    else:
        url = url.value

    async with session.request(method='GET', url=url, params=params) as resp:  # noqa
        data = await resp.json()

        return data


async def batch_game_create(game_ids, class_type, db_conn) -> list:
    """Batch creation for Game objects. This drastically improves performance
        when creating multiple game objects.

    Args:
        db_conn (sqlite3.Connection): Database connection
        game_ids (List of Ints): List of game ids to create game objects
        class_type (BaseGame): Game object type to create.
    Raises:
        URLException: NotImplemented

    Returns:
        dict: A list of game objects containing the json responses of
                each query.
    """
    async with aiohttp.ClientSession() as session:
        workers = []
        for _id in game_ids:
            workers.append(
                _create_game(Url.GAME, _id, class_type, session, db_conn)
            )

        games = await asyncio.gather(*workers)
    return games


async def batch_game_update(games):
    """Batch update for Game objects."""
    async with aiohttp.ClientSession() as session:
        workers = []
        for game in games:
            workers.append(
                _update_game(Url.GAME, game, session)
            )

        await asyncio.gather(*workers)


async def _create_game(url, _id, class_type, session, db_conn):
    """Internal wrapper to create a Game Object"""
    json = await async_request(url, session, url_mods={'game_id': _id})

    if class_type == 'full':
        from .games import FullGame
        game = FullGame(db_conn, _id, json)
    elif class_type == 'banner':
        from .games import BannerGame
        game = BannerGame(db_conn, _id, json)
    else:
        raise ValueError(f'{class_type} is not a valid game type.')

    return game


async def _update_game(url, game, session):
    """Internal wrapper to update a Game object"""
    json = await async_request(url, session, url_mods={'game_id': game.game_id})  # noqa

    game.update_data(json)


def _generate_url(url, url_mods):
    """
    Takes a url and url modifications and creates a full Url
    Used to create a url with unique values (ie. Team, ID, etc.)
    """
    try:
        if Url.GAME == url:
            url = url.value.format(url_mods['game_id'])
        elif Url.TEAMS == url:
            url = url.value.format(url_mods['team_id'])
        elif Url.TEAM_ROSTER == url:
            url = url.value.format(url_mods['team_id'])
        elif Url.PLAYERS == url:
            url = url.value.format(url_mods['player_id'])
    except KeyError as err:
        raise URLException(
            f'Url modifications did not contain the valid format string.\n\
             Got: {url_mods}'
        )
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
