import arrow

from puck.urls import Url
from puck.utils import GAME_STATUS, request
from puck.Teams import GameStatsTeam


class GameIDException(Exception):
    def __init__(self, game_id):
        super().__init__(f'The Game ID supplied ({game_id}) is not valid')


class BannerGame(object):
    """
    The generic Game Class. This class holds basic data about each game. 
    Creation will fail if the game ID doesnt exist.

    Banner should be used in the display of simple data. 

    Data is collected from Url.GAME endpoint.

    TODO: shorten game_info to game_info['gameData'] etc.
    TODO: Write up documentation.
    TODO: Think about using decorators for attributes.
    """

    def __init__(self, game_id=None):
        if not game_id:
            raise GameIDException

        self.game_id = game_id

        game_info = request(Url.GAME, url_mods={'game_id': game_id})

        self.home = GameStatsTeam(self, game_id, 'home', game_info)
        self.away = GameStatsTeam(self, game_id, 'away', game_info)

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

    def update(self):
        """
        This class method updates a game object.
        """

        # If the game is already finished, no need to request info
        if self.is_final:
            return

        game_info = request(Url.GAME, url_mods={'game_id': self.game_id})

        _status_code = int(game_info['gameData']['status']['statusCode'])

        # could check just _status_code, to check if game is still in preview
        # however would prefer to check both just in case
        if _status_code in GAME_STATUS['Preview'] and self.game_status in GAME_STATUS['Preview']:
            # if this check hits, just replace the game_status with _status_code
            # The Preview status code is 1 and 2 and this just updates the code
            # similar to is_final if the game hasn't changed state just return
            self.game_status = _status_code
            return
        else:
            # game state has changed
            self.game_status = _status_code

        # only these values need to be updated
        self.home_score = game_info['liveData']['teams']['home']['goals']
        self.away_score = game_info['liveData']['teams']['away']['goals']
        self.period = game_info['liveData']['linescore']['currentPeriodOrdinal']
        self.time = game_info['liveData']['linescore']['currentPeriodTimeRemaining']
        self.in_intermission = game_info['liveData']['linescore']['intermissionInfo']['inIntermission']

        if self.game_status in GAME_STATUS['Final']:
            self.is_final = True
            self.is_live = False
        else:
            self.is_live = True

    # are these two functions even necessary?
    def is_live(self):
        return self.is_live

    def is_finished(self):
        return self.is_final

    def leading_team(self):
        if self.home_score > self.away_score:
            return self.home_abb
        elif self.away_score > self.home_score:
            return self.away_abb
        else:
            return None

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class FullGame(object):
    """
    The Full Game class is designed to encapsulate MOST of a games stats. 
    BannerGame is for simple data display/collection. This class will hold all
    stats such as shots, saves, powerplays, etc. 

    NOTE: FullGame DOES NOT inherit from BannerGame in large part because it
    would require two requests to the same endpoint. I have some ideas on how
    to circumvent this problem, but it introduces too much complexity.   

    TODO:Finish creation and update function
    """

    def __init__(self, game_id=None):
        if not game_id:
            raise GameIDException

        self.game_id = game_id

        game_info = request(Url.GAME, url_mods={'game_id': game_id})

    def update(self):
        pass


def get_game_ids(params=None):
    """
    Return a list of game ids based on specific url parameters.

    Args:
        params (dict, optional): Misc. url parameters that alter the query.

    Returns:
        list: returns list of game ids for selected query
    """

    game_info = request(Url.SCHEDULE, params=params)

    ids = []
    # dates is a list of all days requested
    # if this key does not exist an empty list will be returned
    for day in game_info.get('dates', []):
        # games is a list of all games in a day
        for game in day.get('games', []):
            ids.append(game['gamePk'])

    return ids
