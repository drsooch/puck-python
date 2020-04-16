import asyncio

import arrow

import puck.constants as const
import puck.parser as parser
from puck.teams import BannerTeam, GameStatsTeam
from puck.urls import Url
from puck.utils import request


class GameIDException(Exception):
    def __init__(self, game_id):
        super().__init__(f'The Game ID supplied ({game_id}) is not valid')


class BaseGame(object):
    """The BaseGame class. This should only be used a parent class
        for user defined game classes.

    Attributes:
        db_conn (psycopg2.Connection): Database Connection
        game_id (int): Game ID
        home (None): Not Implemented
        away (None): Not Implemented
    """

    def __init__(self, db_conn, game_id):
        self.db_conn = db_conn
        self.game_id = game_id
        self.home = None
        self.away = None

    def update_data(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.game_id == other.game_id

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class BannerGame(BaseGame):
    """
    The generic Game Class. This class holds basic data about each game.
    Creation will fail if the game ID doesnt exist.

    Banner should be used in the display of simple data.

    Data is collected from Url.GAME endpoint.

    Inherits:
        BaseGame

    Attributes:
        home (BaseTeam): Team object for the home team
        away (BaseTeam): Team object for the away team
        game_status (int): Status code for where the game is at
        start_time (str): String formatted from an Arrow object
        game_date (Arrow): An Arrow object holding the date
        period (str): Indicates the current period
        time (str): Indicates time left in the period
        in_intermission (bool): Boolean indicating if game is in intermission
        is_preview (bool): Boolean indicating if game is in preview
        is_final (bool): Boolean indicating if game is final
        is_live (bool): Boolean indicating if game is live
    """

    def __init__(self, db_conn, game_id, data=None, _class=BannerTeam):
        """
        Args:
            db_conn (psycopg2.Connection): database connection
            game_id (int): Game ID
            data (dict, optional): JSON rep of the game. Defaults to None.
            _class (BaseTeam, optional): Team object to create.
                Defaults to BannerTeam.
        """
        super().__init__(db_conn, game_id)

        if not data:
            data = request(Url.GAME, url_mods={'game_id': game_id})

        parsed_data = parser.game(data)

        for key, val in parsed_data.items():
            setattr(self, key, val)

        self.home = _class(self, game_id, 'home', data)
        self.away = _class(self, game_id, 'away', data)

    def update_data(self, data=None):
        """
        This class method updates a game object.

        NOTE: Does not use game as we only need to update small
        subset of data.
        """

        # TODO CLEAN UP UPDATE

        # If the game is already finished, no need to request info
        if self.is_final:
            return

        if not data:
            data = request(Url.GAME, url_mods={'game_id': self.game_id})

        _status_code = int(data['gameData']['status']['statusCode'])

        # game status hasn't changed
        if _status_code in const.GAME_STATUS['Preview'] and self.is_preview:  # noqa
            self.game_status = _status_code
            return

        parsed_data = parser.game(data)

        for key, val in parsed_data.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise AttributeError(
                    f'Game.update_data received an attribute {key} \
                    that has not been set.'
                )

        # this will call update no matter the Team Class type
        self.home.update_data(data)
        self.away.update_data(data)


class FullGame(BannerGame):
    """
    The Full Game is an exact copy of BannerGames with a few minor exceptions.
    BannerGame defaults to BannerTeam as it's Team Implementation. This class
    uses GameStatsTeam. This class also has an additional wrapper method to
    instantiate the Players of each team.

    Inherits:
        BannerGame

    Attributes:
        Same as BannerGame.

    NOTE: This class is mostly for clarifying to the puck interface
    what kind of player data we can end up with.

    """

    def __init__(self, db_conn, game_id, data=None):
        if not data:
            data = request(Url.GAME, url_mods={'game_id': game_id})

        super().__init__(db_conn=db_conn, game_id=game_id, data=data, _class=GameStatsTeam)  # noqa

    def update_data(self, data=None):
        super().update_data(data)

    def init_players(self, data=None):
        """Wrapper to init both home and away players"""

        # if the internal team object is not GameStatsTeam we ignore the call
        if isinstance(self.home, GameStatsTeam):
            self.home.init_players(data)
            self.away.init_players(data)


def get_game_ids(url_mods=None, params=None):
    """
    Return a list of game ids based on specific url parameters.

    Args:
        url_mods (dict, optional): Certain urls are required to be formatted
        params (dict, optional): Misc. url parameters that alter the query.

    Returns:
        list: returns list of game ids for selected query
    """

    game_info = request(Url.SCHEDULE, url_mods=url_mods, params=params)

    ids = []
    # dates is a list of all days requested
    # if this key does not exist an empty list will be returned
    for day in game_info.get('dates', []):
        # games is a list of all games in a day
        for game in day.get('games', []):
            ids.append(game['gamePk'])

    return ids
