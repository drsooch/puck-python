import arrow
import click

from puck.urls import Url
from puck.utils import get_url


class GameIDException(Exception):
    pass


class BaseGame(object):
    def __init__(self, **kwargs):
        if kwargs.get('gamePk'):
            self.game_id = kwargs.get('gamePk')
        else:
            raise GameIDException

        # maybe use get method?
        self.home_team = kwargs['teams']['home']['team']['name']
        self.away_team = kwargs['teams']['away']['team']['name']
        self.home_score = kwargs['teams']['home']['score']
        self.away_score = kwargs['teams']['away']['score']
        self.game_status = kwargs['status']['abstractGameState']

        # get this value in case game has not started
        self.game_start = arrow.get(kwargs['gameDate']).strftime('%I:%M %p %Z')

    def _get_game_info(self):

        pass


class VerboseGame(BaseGame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def games_handler(conf, cmd_vals):
    '''
    Handles all of "puck games [option]" adding url parameters if needed

    TODO: Handle the fact that Pre-Season games are not queried unless "?date="
    is used.

    NOTE: The elif check for 'date' may cause a bug in the future. 'date' is a
    url parameter and could possibly alter state.
    '''

    if 'yesterday' in cmd_vals:
        _yesterday(cmd_vals)

    elif 'tomorrow' in cmd_vals:
        _tomorrow(cmd_vals)

    elif 'date' in cmd_vals:
        _date(cmd_vals)

    elif 'date_range' in cmd_vals:
        _date_range(cmd_vals)

    else:
        pass

    games_query(conf, cmd_vals)


def _yesterday(cmd_vals):
    '''
    Properly format the url paramaters for -y/--yesterday.
    The value passed will be altered.
    '''
    # get local date and check schedule using yesterday's date
    yest = arrow.now().shift(day=-1)
    yest = yest.strftime('%Y-%m-%d')

    # add the date url parameter
    cmd_vals.setdefault('date', yest)


def _tomorrow(cmd_vals):
    '''
    Properly format the url paramaters for --tomorrow.
    The value passed will be altered.
    '''
    # get local date and check schedule using tomorrow's date
    tmrw = arrow.now().shift(days=1)
    tmrw = tmrw.strftime('%Y-%m-%d')

    # add the date url parameter
    cmd_vals.update({'date': tmrw})


def _date(cmd_vals):
    '''
    Properly format the url parameters for -d/--date.
    The value passed will be altered.


    NOTE: The date strings should already be checked for validity. 
        No need to check again.
    '''

    _date = cmd_vals.pop('date')
    _date = arrow.get(_date).strftime('%Y-%m-%d')

    cmd_vals.update({'date': _date})


def _date_range(cmd_vals):
    '''
    Properly format the url parameters for --date-range.
    The value passed will be altered.

    NOTE: The date strings should already be checked for validity. 
        No need to check again.
    '''
    # put dates in comparable format
    dr = cmd_vals.pop('start_date')
    dr0 = arrow.get(dr[0]).strftime('%Y-%m-%d')
    dr1 = arrow.get(dr[1]).strftime('%Y-%m-%d')

    # sauce em into a tuple for s's and g's
    dr = (dr0, dr1)

    # replaces/adds the startDate and endDate url parameters
    cmd_vals.update({'startDate': min(dr)})
    cmd_vals.update({'endDate': max(dr)})


def _today(cmd_vals):
    _date = arrow.now().strftime('%Y-%m-%d')

    cmd_vals.update({'date': _date})


def games_query(conf, url_mods=None, params=None):
    resp = get_url(Url.SCHEDULE, url_mods=None, params=params)

    normal_games_echo(resp)


def verbose_games_echo(_json):
    g_list = [x for x in _json['dates'][0]['games']]
    pass


def normal_games_echo(_json):
    g_list = [x for x in _json['dates'][0]['games']]

    pass
