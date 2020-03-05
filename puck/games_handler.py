import asyncio

import arrow
import click

from puck.games import BannerGame, FullGame, get_game_ids
from puck.urls import Url
from puck.utils import batch_game_create, request, team_to_id


def games_handler(config, cmd_vals):
    """
    Handles all of "puck games [option]" adding url parameters if needed

    NOTE: The elif check for 'date' may cause a bug in the future. 'date' is a
    url parameter and could possibly alter state.

    Arguments:
        config (Config): the Config object
        cmd_vals (dict): Args and Options passed through the command line

    Returns:
        None
    """

    if 'yesterday' in cmd_vals:
        _yesterday(cmd_vals)

    elif 'tomorrow' in cmd_vals:
        _tomorrow(cmd_vals)

    elif 'date' in cmd_vals:
        _date(cmd_vals)

    elif 'date_range' in cmd_vals:
        _date_range(cmd_vals)

    else:
        _today(cmd_vals)

    if 'team' in cmd_vals:
        team_id = team_to_id(cmd_vals.pop('team'))
        cmd_vals.update({'teamId': team_id})

    if config.verbose:
        verbose_games_echo()
    else:
        normal_games_echo(config.conn, cmd_vals)


def _yesterday(cmd_vals):
    """
    Properly format the url paramaters for -y/--yesterday.
    The value passed will be altered.
    """
    # get local date and check schedule using yesterday's date
    yest = arrow.now().shift(days=-1)
    yest = yest.strftime('%Y-%m-%d')

    # add the date url parameter
    cmd_vals.update({'date': yest})


def _tomorrow(cmd_vals):
    """
    Properly format the url paramaters for --tomorrow.
    The value passed will be altered.
    """
    # get local date and check schedule using tomorrow's date
    tmrw = arrow.now().shift(days=1)
    tmrw = tmrw.strftime('%Y-%m-%d')

    # add the date url parameter
    cmd_vals.update({'date': tmrw})


def _date(cmd_vals):
    """
    Properly format the url parameters for -d/--date.
    The value passed will be altered.


    NOTE: The date strings should already be checked for validity.
        No need to check again.
    """

    _date = cmd_vals.pop('date')
    _date = arrow.get(_date).strftime('%Y-%m-%d')

    cmd_vals.update({'date': _date})


def _date_range(cmd_vals):
    """
    Properly format the url parameters for --date-range.
    The value passed will be altered.

    NOTE: The date strings should already be checked for validity.
        No need to check again.
    """
    # put dates in comparable format
    dr = cmd_vals.pop('date_range')
    dr0 = arrow.get(dr[0]).strftime('%Y-%m-%d')
    dr1 = arrow.get(dr[1]).strftime('%Y-%m-%d')

    # sauce em into a tuple for s's and g's
    dr = (dr0, dr1)

    # replaces/adds the startDate and endDate url parameters
    cmd_vals.update({'startDate': min(dr)})
    cmd_vals.update({'endDate': max(dr)})


def _today(cmd_vals):
    """
    Properly format the url parameters for the -t/--today or no options.
    The value passed will be altered.

    NOTE: The date strings should already be checked for validity.
        No need to check again.
    """
    _date = arrow.now().strftime('%Y-%m-%d')

    cmd_vals.update({'date': _date})


def verbose_games_echo(games):
    pass


def normal_games_echo(db_conn, params=None):
    game_ids = get_game_ids(params=params)

    games_list = asyncio.run(
        batch_game_create(game_ids, 'banner', db_conn)
    )

    build_norm_output(games_list)


def build_norm_output(g_list):
    gen_format = '{:^10} | {:^15} | {:^10}'

    title = gen_format.format('Away ', 'Period', 'Home')
    click.echo(title)

    for g in g_list:
        _away = g.away.abbreviation + ' ' + str(g.away.goals)
        _home = g.home.abbreviation + ' ' + str(g.home.goals)

        if g.is_live or g.is_final:
            _time = g.time + ' - ' + g.period
        else:
            _time = g.start_time

        output = gen_format.format(_away, _time, _home)

        click.echo(output)
