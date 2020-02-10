import arrow

from .urls import Url
from .utils import GAME_STATUS, request
from .teams import FullStatsTeam, BannerTeam


class GameIDException(Exception):
    def __init__(self, game_id):
        super().__init__(f'The Game ID supplied ({game_id}) is not valid')


class BaseGame(object):
    """The BaseGame class. This should only be used a parent class
        for user defined game classes.

    NOTE: This class is not fully implemented and may never be. Currently
        here for possibilities.
    """

    def __init__(self, game_id):
        self.game_id = game_id
        self.home = None
        self.away = None

    def __eq__(self, other):
        return self.game_id == other.game_id

    def update(self):
        raise NotImplementedError()

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

    def __init__(self, game_id, game_info=None, team_class=BannerTeam):
        super().__init__(game_id)
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        self.home = team_class(self, game_id, 'home', game_info)
        self.away = team_class(self, game_id, 'away', game_info)

        self.game_status = int(game_info['gameData']['status']['statusCode'])
        self.start_time = arrow.get(
            game_info['gameData']['datetime']['dateTime']
        ).to('local').strftime('%I:%M %p %Z')
        self.game_date = arrow.get(
            game_info['gameData']['datetime']['dateTime']
        ).to('local').date()

        if self.game_status in GAME_STATUS['Preview']:
            # if the game is in Preview keys won't exist
            self.period = None
            self.time = None
            self.in_intermission = False
            self.is_live = False
            self.is_final = False
            self.is_preview = True
        else:
            self.period = game_info['liveData']['linescore']['currentPeriodOrdinal']  # noqa
            self.time = game_info['liveData']['linescore']['currentPeriodTimeRemaining']  # noqa
            self.in_intermission = game_info['liveData']['linescore']['intermissionInfo']['inIntermission']  # noqa
            self.is_preview = False

            if self.game_status in GAME_STATUS['Final']:
                self.is_final = True
                self.is_live = False
            else:
                self.is_final = False
                self.is_live = True

    def update(self, game_info=None):
        """
        This class method updates a game object.
        """

        # If the game is already finished, no need to request info
        if self.is_final:
            return

        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': self.game_id})

        _status_code = int(game_info['gameData']['status']['statusCode'])

        # game status hasn't changed
        if _status_code in GAME_STATUS['Preview'] and self.is_preview:  # noqa
            self.game_status = _status_code
            return
        else:
            # game state has changed
            self.game_status = _status_code
            self.is_preview = False

            if self.game_status in GAME_STATUS['Final']:
                self.is_final = True
                self.is_live = False
            else:
                self.is_live = True

        # only these values need to be updated
        self.period = game_info['liveData']['linescore']['currentPeriodOrdinal']  # noqa
        self.time = game_info['liveData']['linescore']['currentPeriodTimeRemaining']  # noqa
        self.in_intermission = game_info['liveData']['linescore']['intermissionInfo']['inIntermission']  # noqa

        # this will call update no matter the Team Class type
        self.home.update(game_info)
        self.away.update(game_info)


class FullGame(BannerGame):
    """
    The Full Game class is designed to encapsulate MOST of a games stats.
    BannerGame is for simple data display/collection. This class will hold all
    stats such as shots, saves, powerplays, etc.

    """

    def __init__(self, game_id, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        super().__init__(game_id=game_id, game_info=game_info, team_class=FullStatsTeam)  # noqa

    def update(self, game_info=None):
        super().update(game_info)


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
