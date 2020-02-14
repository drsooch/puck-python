from .urls import Url
from .utils import GAME_STATUS, request
from collections import UserDict, UserList


class TeamIDException(Exception):
    def __init__(self, _id=None):
        super().__init__('Invalid Team ID of {_id}')


class InvalidTeamType(Exception):
    def __init__(self):
        super().__init__('Invalid team_type, must be either "home" or "away"')


class BaseTeam(object):
    """
    BaseTeam object holds all data retrieved from api_endpoint/teams/{ID}
    NOTE: The current implementation does not retrieve from the endpoint above.
        Must pass the data directly to the object.

    Attributes:
        team_id (int): API ID number for a team
        long_name (str): A team's full name
        abbreviation (str): 3-Letter team abbreviation
        division (str): Full name of a team's division
        conference (str): Full name of a team's conference
        team_url (str): A team's home page url

    Raises:
        InvalidTeamType: Creation fails when an invalid team type is passed
    """

    def __init__(self, team_data, team_type):
        """Constructor for BaseTeam.

        Args:
            team_id (int): API ID number for a team
            team_type (str): Either "home" or "away"

        Raises:
            InvalidTeamType
        """
        team_type = team_type.lower()

        if team_type != 'home' and team_type != 'away':
            raise InvalidTeamType

        # shortens the json "tree"
        team_data = team_data['gameData']['teams'][team_type]

        self.team_id = team_data['id']
        self.long_name = team_data['name']
        self.abbreviation = team_data['abbreviation']
        self.division = team_data['division']['name']
        self.conference = team_data['conference']['name']
        self.team_url = team_data['officialSiteUrl']

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class BannerTeam(BaseTeam, UserDict):
    """Simple Team class for "banner" display.

    Attributes:
        goals (int): a team's goals
        team_type (str): "home" or "away"
        _game (Game): Any object that inherits a game type.
            The parent container that holds reference to this object.

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
        BaseTeam.__init__(self, game_info, team_type)

        self._game = game
        self.game_id = game_id

        # use UserDict as a parent class to match FullStatsTeam class
        UserDict.__init__(
            self,
            {
                'goals': game_info['liveData']['linescore']['teams'][team_type]['goals']  # noqa
            }
        )

    def update_data(self, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        self.update({
            'goals': game_info['liveData']['linescore']['teams'][self.team_type]['goals']  # noqa
        })


class FullStatsTeam(BaseTeam, UserDict):
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
        BaseTeam.__init__(self, game_info, team_type)

        # holds reference to the Game "container"
        self._game = game
        self.game_id = game_id

        # put the team skater stats into an internal dict object
        UserDict.__init__(
            self,
            game_info['liveData']['boxscore']['teams'][self.team_type]['teamStats']['teamSkaterStats']  # noqa
        )

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

        self.player_stats = None  # TODO: player stats.

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
        if _status_code in GAME_STATUS['Preview'] and self._game.game_status in GAME_STATUS['Preview']:  # noqa
            # end update early as game is still in preview
            # see BannerGame.update() on discussion for why this check
            # is the way it is
            return

        # calls UserDict update method for internal dict
        self.update(
            game_info['liveData']['boxscore']['teams'][self.team_type]['teamStats']['teamSkaterStats']  # noqa
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

    def __init__(self, periods, team_type=None):
        self.num_per = len(periods)

        data = []
        for i in range(self.num_per):
            name = periods[i]['ordinalNum']
            data.append(
                Period(name, periods[i][team_type])
            )

        super().__init__(data)

        self.total_shots = sum([x['shotsOnGoal'] for x in self.data])

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

        self.total_shots = sum([x['shotsOnGoal'] for x in self.data])

        pass

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class Period(UserDict):
    """Internal Use Only. Used for better accessing period stats."""

    def __init__(self, name, data):
        self.name = name
        if data:
            data.pop('rinkSide')
        super().__init__(data)

    def update_data(self, data):
        if data:
            data.pop('rinkSide')

        # calls UserDict updates
        self.update(data)

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class ShootoutStats(object):
    """Internal Use Only. Used for better accessing shootout stats."""

    def __init__(self, goals=None, attempts=None):
        self.goals = goals
        self.attempts = attempts

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'
