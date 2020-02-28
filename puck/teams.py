from collections import UserDict, UserList

from .urls import Url
from .utils import request
from .player import GamePlayer, PlayerCollection
import puck.parser as parser
from puck.database.db import select_stmt
import puck.database.db_constants as db_const
import puck.constants as const


class TeamIDException(Exception):
    def __init__(self, _id=None):
        super().__init__('Invalid Team ID of {_id}')


class InvalidTeamType(Exception):
    def __init__(self):
        super().__init__('Invalid team_type, must be either "home" or "away"')


class BaseTeam(object):
    """
    BaseTeam object holds all data retrieved from the internal database
        Must pass the data directly to the object.

    Attributes:
        team_id (int): API ID number for a team
        full_name (str): A team's full name
        abbreviation (str): 3-Letter team abbreviation
        division (int): Integer denoting a team's division
        conference (int): Integer denoting a team's conference

    Raises:
        InvalidTeamType: Creation fails when an invalid team type is passed
    """

    def __init__(self, team_id, db_conn):
        """Constructor for BaseTeam.

        Args:
            team_id (int): API ID number for a team
            db_conn (sqlite3.Connection): Connection object to the database
        Raises:
            InvalidTeamType
        """

        # get data from internal database
        team_data = select_stmt(
            db_conn, 'team', db_const.TableColumns.BASE_GAME_COLS,
            where=[('team_id', team_id)]
        )

        # create attributes
        for key in team_data[0].keys():
            setattr(self, key, team_data[0][key])

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class BannerTeam(BaseTeam):
    """Simple Team class for "banner" display.

    Attributes:
        goals (int): a team's goals
        team_type (str): "home" or "away"
        _game (Game): The parent container that holds reference to this object.

    Raises:
        InvalidTeamType: If 'home' or 'away' is not supplied
        creation will fail.
    """

    def __init__(self, game, game_id, team_type, game_info=None):
        """Constructor for BannerTeam

        Args:
            game (BannerGame): Any game that inherits BannerGame
            game_id (int): API Game ID
            team_type (str): Either "home" or "away"
            game_info (dict, optional): JSON API response represented as a
                dictionary. Defaults to None.

        Raises:
            InvalidTeamType: If 'home' or 'away' is not supplied
                creation will fail.
        """

        # housekeeping
        team_type = team_type.lower()
        if team_type == 'home' or team_type == 'away':
            self.team_type = team_type
        else:
            raise InvalidTeamType

        # check if game data was passed
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        # get the teams id number
        team_id = game_info['gameData']['teams'][team_type]['id']

        # call parent class constructor
        super().__init__(team_id, game.db_conn)

        self.game = game
        self.game_id = game_id

        # parse the game data
        parsed_data = parser.teams_skater_stats_parser(
            game_info, self.team_type, False
        )

        # set attributes (goals in this case)
        for key, val in parsed_data.items():
            setattr(self, key, val)

    def update_data(self, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        parsed_data = parser.teams_skater_stats_parser(
            game_info, self.team_type, False
        )

        for key, val in parsed_data.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise AttributeError(
                    f'Update received an attribute {key} \
                    that has not been set.'
                )


class FullStatsTeam(BaseTeam):
    """
    This class is designed for use in conjuction with a FullGame object.
    Built upon the BaseTeam class, this class gathers stats relevant to
    whatever game its attached to.

    Data is collected from the Url.GAME endpoint.

    Inherits:
        BaseTeam: This is the base Team class

    Attributes:
        TODO

    Raises:
        InvalidTeamType: If 'home' or 'away' is not supplied
        creation will fail.
    """

    def __init__(self, game, game_id, team_type, game_info=None):
        """Constructor for GameStatsTeam

        Args:
            game (BannerGame or FullGame): The Container object. Any object
                                           that inherits BannerGame
            game_id (int): API Game ID
            team_type (str): Either 'home' or 'away'
            game_info (dict, optional): JSON API response represented as
                                        a dictionary

        Raises:
            InvalidTeamType: If 'home' or 'away' is not supplied
                creation will fail.
        """

        # housekeeping check
        team_type = team_type.lower()
        if team_type == 'home' or team_type == 'away':
            self.team_type = team_type
        else:
            raise InvalidTeamType

        # if the game data was passed to the constructor use that
        if not game_info:
            # request the game data
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        # get the teams id number
        team_id = game_info['gameData']['teams'][team_type]['id']

        # Call the parent class constructor
        super().__init__(team_id, game.db_conn)

        # holds reference to the Game "container"
        self.game = game
        self.game_id = game_id

        # parse the data
        parsed_data = parser.teams_skater_stats_parser(
            game_info, self.team_type, True
        )

        # set attributes
        for key, val in parsed_data.items():
            setattr(self, key, val)

        # PeriodStats object for easier referencing
        self.periods = PeriodStats(
            game_info['liveData']['linescore']['periods'], team_type
        )

        # ShootOutStats object for easier referencing
        if game_info['liveData']['linescore']['hasShootout']:
            self.shootout = ShootoutStats(
                goals=game_info['liveData']['linescore']['shootoutInfo'][team_type]['scores'],  # noqa
                attempts=game_info['liveData']['linescore']['shootoutInfo'][team_type]['attempts']  # noqa
            )
        else:
            self.shootout = ShootoutStats()

        id_list = game_info['liveData']['boxscore']['teams'][team_type]['goalies']  # noqa
        id_list.extend(game_info['liveData']['boxscore']['teams'][team_type]['skaters'])  # noqa
        id_list.extend(game_info['liveData']['boxscore']['teams'][team_type]['scratches'])  # noqa

        self.players = PlayerCollection(
            self, id_list, _class=GamePlayer
        )

    def update_data(self, game_info=None):
        """Updates an object using fresh data.

        Args:
            game_info (dict, optional): JSON API response represented as
                                        a dictionary. Defaults to None.
        """

        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        _status_code = int(game_info['gameData']['status']['statusCode'])

        # NOTE: This check could fail if the game status code
        #       is updated before this.
        if _status_code in const.GAME_STATUS['Preview'] and self._game.game_status in const.GAME_STATUS['Preview']:  # noqa
            return

        parsed_data = parser.teams_skater_stats_parser(
            game_info, self.team_type, True
        )

        for key, val in parsed_data.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise AttributeError(
                    f'Update received an attribute {key} \
                    that has not been set.'
                )

        self.periods.update_data(
            game_info['liveData']['linescore']['periods'],
            self.team_type
        )

        if game_info['liveData']['linescore']['hasShootout']:
            self.shootout.goals = game_info['liveData']['linescore']['shootoutInfo'][team_type]['scores']  # noqa
            self.shootout.attempts = game_info['liveData']['linescore']['shootoutInfo'][team_type]['attempts']  # noqa


class PeriodStats(UserList):
    """
    Internal Use Only.

    This class is for easy use to call individual period stats.
    The current implementation is intended to change.

    NOTE:
        Playoff games can have multiple overtimes, which is not captured
        in this class.

    Attributes:
        first (Period): Contains first period stats
        second (Period): Contains second period stats
        third (Period): Contains third period stats
        ot (Period): Contains fourth period stats

    TODO:
        Model playoffs better.
    """

    def __init__(self, periods, team_type):
        self.num_per = len(periods)

        data = []
        for i in range(self.num_per):
            name = periods[i]['ordinalNum']
            data.append(
                Period(name, periods[i][team_type])
            )

        super().__init__(data)

        self.total_shots = sum([x.shots for x in self.data])

    def update_data(self, periods, team_type):
        _range = len(periods)
        old_count = self.num_per

        if self.num_per < _range:
            self.num_per = _range

        for i in range(self.num_per):
            if i < old_count:
                self.data[i].update_data(periods[i][team_type])
            else:
                name = periods[i]['ordinalNum']
                self.data.append(Period(name, periods[i][team_type]))

        self.total_shots = sum([x.shots for x in self.data])

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class Period(object):
    """Internal Use Only. Used for better accessing period stats."""

    def __init__(self, name, data):
        self.name = name

        parsed_data = parser.period_parser(data)

        for key, val in parsed_data.items():
            setattr(self, key, val)

    def update_data(self, data):
        parsed_data = parser.period_parser(data)

        for key, val in parsed_data.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                AttributeError(
                    f'Period update received an attribute {key} \
                    that has not been set.'
                )

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class ShootoutStats(object):
    """Internal Use Only. Used for better accessing shootout stats."""

    def __init__(self, goals=None, attempts=None):
        self.goals = goals
        self.attempts = attempts

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'
