import arrow

from puck.urls import Url
from puck.utils import GAME_STATUS, request
from puck.Teams import FullStatsTeam, BannerTeam


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

    def update(self):
        raise NotImplementedError()


class BannerGame(object):
    """
    The generic Game Class. This class holds basic data about each game. 
    Creation will fail if the game ID doesnt exist.

    Banner should be used in the display of simple data. 

    Data is collected from Url.GAME endpoint.

    TODO: Write up documentation.
    """

    def __init__(self, game_id, team_class=BannerTeam, game_info=None, inherits=False):
        self.game_id = game_id

        start_r = arrow.now()
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})
        print('request took: ' + str(arrow.now() - start_r))

        start_i = arrow.now()
        self.home = team_class(self, game_id, 'home', game_info)
        self.away = team_class(self, game_id, 'away', game_info)

        self.game_status = int(game_info['gameData']['status']['statusCode'])
        self.start_time = arrow.get(
            game_info['gameData']['datetime']['dateTime']
        ).to('local').strftime('%I:%M %p %Z')

        if self.game_status in GAME_STATUS['Preview']:
            # if the game is in Preview keys won't exist
            self.period = None
            self.time = None
            self.in_intermission = False
            self.is_live = False
            self.is_final = False
        else:
            self.period = game_info['liveData']['linescore']['currentPeriodOrdinal']
            self.time = game_info['liveData']['linescore']['currentPeriodTimeRemaining']
            self.in_intermission = game_info['liveData']['linescore']['intermissionInfo']['inIntermission']

            if self.game_status in GAME_STATUS['Final']:
                self.is_final = True
                self.is_live = False
            else:
                self.is_final = False
                self.is_live = True

        print('Init took: ' + str(arrow.now() - start_i))

    def update(self):
        """
        This class method updates a game object.
        """

        # If the game is already finished, no need to request info
        if self.is_final:
            return

        game_info = request(Url.GAME, url_mods={'game_id': self.game_id})

        _status_code = int(game_info['gameData']['status']['statusCode'])

        # game status hasn't changed
        if _status_code in GAME_STATUS['Preview'] and self.game_status in GAME_STATUS['Preview']:
            self.game_status = _status_code
            return
        else:
            # game state has changed
            self.game_status = _status_code

        # only these values need to be updated
        self.period = game_info['liveData']['linescore']['currentPeriodOrdinal']
        self.time = game_info['liveData']['linescore']['currentPeriodTimeRemaining']
        self.in_intermission = game_info['liveData']['linescore']['intermissionInfo']['inIntermission']

        # this will call update no matter the Team Class type
        self.home.update(game_info)
        self.away.update(game_info)

        if self.game_status in GAME_STATUS['Final']:
            self.is_final = True
            self.is_live = False
        else:
            self.is_live = True

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class FullGame(BannerGame):
    """
    The Full Game class is designed to encapsulate MOST of a games stats. 
    BannerGame is for simple data display/collection. This class will hold all
    stats such as shots, saves, powerplays, etc. 

    """

    def __init__(self, game_id, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        super().__init__(game_id, team_class=FullStatsTeam, game_info=game_info)

    def update(self):
        super().update()


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
