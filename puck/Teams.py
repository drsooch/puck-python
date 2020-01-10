from .urls import Url
from .utils import GAME_STATUS, request


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

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class BannerTeam(BaseTeam):
    """Simple Team class for "banner" display.

    Attributes:
        goals (int): a team's goals
        team_type (str): "home" or "away"
        _game (Game): Any object that inherits a game type. The parent container that holds
            reference to this object. 

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
            game_info (dict, optional): JSON API response represented as dictionary.
                Defaults to None.

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
        super().__init__(game_info, team_type)

        self._game = game
        self.game_id = game_id

        # the only data we need to track.
        self.goals = game_info['liveData']['linescore']['teams'][team_type]['goals']

    def update(self, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        self.goals = game_info['liveData']['linescore']['teams'][self.team_type]['goals']


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
            game (BannerGame or FullGame): The Container object. Any object that inherits BannerGame
            game_id (int): API Game ID
            team_type (str): Either 'home' or 'away'
            game_info (dict, optional): JSON API response represented as dictionary

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
        super().__init__(game_info, team_type)

        # holds reference to the Game "container"
        self._game = game
        self.game_id = game_id

        # invoke internal setter method
        self._set(game_info)

        # PeriodStats object for easier referencing
        self.periods = PeriodStats(
            game_info['liveData']['linescore']['periods'], team_type
        )

        # ShootOutStats object for easier referencing
        if game_info['liveData']['linescore']['hasShootout']:
            self.shootout = ShootoutStats(
                goals=game_info['liveData']['linescore']['shootoutInfo'][team_type]['scores'],
                attempts=game_info['liveData']['linescore']['shootoutInfo'][team_type]['attempts']
            )
        else:
            self.shootout = ShootoutStats()

        self.player_stats = None  # TODO: player stats.

    def update(self, game_info=None):
        """Updates an object using fresh data. 

        Args:
            game_info (dict, optional): JSON API response represented as dictionary. Defaults to None.
        """

        # if no json is passed.
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        _status_code = int(game_info['gameData']['status']['statusCode'])

        # NOTE: This check could fail if the game status code is updated before this.
        if _status_code in GAME_STATUS['Preview'] and self._game.game_status in GAME_STATUS['Preview']:
            # end update early as game is still in preview
            # see BannerGame.update() on discussion for why this check is the way it is
            return

        # invoke internal set methods
        self._set(game_info)
        self.periods.update(
            game_info['liveData']['linescore']['periods'],
            self.team_type
        )

        if game_info['liveData']['linescore']['hasShootout']:
            self.shootout.goals = game_info['liveData']['linescore']['shootoutInfo'][team_type]['scores']
            self.shootout.attempts = game_info['liveData']['linescore']['shootoutInfo'][team_type]['attempts']

    def _set(self, game_info):
        """Internal Use Only. The main code for setting/updating values"""
        # shortened JSON paths
        live_data = game_info['liveData']
        team_stats = game_info['liveData']['boxscore']['teams'][self.team_type]['teamStats']['teamSkaterStats']

        # could just use team_data['teamStats']['teamSkaterStats']
        # but choosing to make each an attribute
        self.goals = team_stats['goals']
        self.pims = team_stats['pim']
        self.shots = team_stats['shots']
        self.pp_pct = float(
            team_stats['powerPlayPercentage']
        )
        self.pp_goals = team_stats['powerPlayGoals']
        self.pp_att = team_stats['powerPlayOpportunities']
        self.faceoff_pct = float(
            team_stats['faceOffWinPercentage']
        )
        self.blocked_shots = team_stats['blocked']
        self.takeaways = team_stats['takeaways']
        self.giveaways = team_stats['giveaways']
        self.hits = team_stats['hits']

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class PeriodStats(object):
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

    def __init__(self, periods=None, team_type=None):
        self.first = Period()
        self.second = Period()
        self.third = Period()
        self.ot = Period()

        self._set(periods, team_type)

    # for ease of reference
    def update(self, periods, team_type):
        self._set(periods, team_type)

    def _set(self, periods, team_type):
        """Internal Use Only. The main code for setting/updating values"""
        for per in periods:
            if per['num'] == 1:
                self.first.goals = per[team_type]['goals']
                self.first.shots = per[team_type]['shotsOnGoal']
            elif per['num'] == 2:
                self.second.goals = per[team_type]['goals']
                self.second.shots = per[team_type]['shotsOnGoal']
            elif per['num'] == 3:
                self.third.goals = per[team_type]['goals']
                self.third.shots = per[team_type]['shotsOnGoal']
            # This needs to be fixed for playoffs.
            else:
                self.ot.goals = per[team_type]['goals']
                self.ot.shots = per[team_type]['shotsOnGoal']

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class Period(object):
    """Internal Use Only. Used for better accessing period stats."""

    def __init__(self, goals=None, shots=None):
        self.goals = goals
        self.shots = shots

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class ShootoutStats(object):
    """Internal Use Only. Used for better accessing shootout stats."""

    def __init__(self, goals=None, attempts=None):
        self.goals = goals
        self.attempts = attempts

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'
