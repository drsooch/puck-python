import arrow
import asyncio


from .urls import Url
from .utils import request
from .teams import FullStatsTeam, BannerTeam
import puck.parser as parser
import puck.constants as const


class GameIDException(Exception):
    def __init__(self, game_id):
        super().__init__(f'The Game ID supplied ({game_id}) is not valid')


class BaseGame(object):
    """The BaseGame class. This should only be used a parent class
        for user defined game classes.
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

    TODO: Write up documentation.
    """

    def __init__(self, db_conn, game_id, data=None, _class=BannerTeam):
        super().__init__(db_conn, game_id)

        if not data:
            data = request(Url.GAME, url_mods={'game_id': game_id})

        parsed_data = parser.game_parser(data)

        for key, val in parsed_data.items():
            setattr(self, key, val)

        self.home = _class(self, game_id, 'home', data)
        self.away = _class(self, game_id, 'away', data)

    def update_data(self, data=None):
        """
        This class method updates a game object.

        NOTE: Does not use game_parser as we only need to update small
        subset of data.
        """

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
        else:
            # game state has changed
            self.game_status = _status_code
            self.is_preview = False

            if self.game_status in const.GAME_STATUS['Final']:
                self.is_final = True
                self.is_live = False
            else:
                self.is_live = True

        # only these values need to be updated
        self.period = data['liveData']['linescore']['currentPeriodOrdinal']  # noqa
        self.time = data['liveData']['linescore']['currentPeriodTimeRemaining']  # noqa
        self.in_intermission = data['liveData']['linescore']['intermissionInfo']['inIntermission']  # noqa

        # this will call update no matter the Team Class type
        self.home.update_data(data)
        self.away.update_data(data)


class FullGame(BannerGame):
    """
    The Full Game class is designed to encapsulate MOST of a games stats.
    BannerGame is for simple data display/collection. This class will hold all
    stats such as shots, saves, powerplays, etc.

    """

    def __init__(self, db_conn, game_id, data=None):
        if not data:
            data = request(Url.GAME, url_mods={'game_id': game_id})

        super().__init__(db_conn=db_conn, game_id=game_id, data=data, _class=FullStatsTeam)  # noqa

    def update_data(self, data=None):
        super().update_data(data)


def get_game_ids(url_mods=None, params=None):
    """
    Return a list of game ids based on specific url parameters.

    Args:
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


# class GamesCollection(UserList):
    # def __init__(self, _ids, game_type):
    # super().__init__(initlist)
#
    # def update_data(self):
    # asyncio.run(batch_request_update(self.data))
#
    # def create(self)
    # asyncio.run(batch_request_create(self.game_ids, game_type))
