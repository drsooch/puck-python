from collections import UserDict, UserList

import puck.constants as const
import puck.database.db_constants as db_const
import puck.parser as parser
from puck.database.db import select_stmt
from puck.player import GamePlayer, PlayerCollection
from puck.urls import Url
from puck.utils import request, get_precision


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
            db_conn, 'team', db_const.TableColumns.BASE_TEAM_CLASS,
            where=('team_id', team_id)
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
        parsed_data = parser.teams_skater_stats(
            game_info, self.team_type, False
        )

        # set attributes (goals in this case)
        for key, val in parsed_data.items():
            setattr(self, key, val)

    def update_data(self, game_info=None):
        if not game_info:
            game_info = request(Url.GAME, url_mods={'game_id': game_id})

        parsed_data = parser.teams_skater_stats(
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


class GameStatsTeam(BaseTeam):
    """
    This class is designed for use in conjuction with a FullGame object.
    Built upon the BaseTeam class, this class gathers stats relevant to
    whatever game its attached to.

    Data is collected from the Url.GAME endpoint.

    Inherits:
        BaseTeam: This is the base Team class

    Attributes:

    Raises:
        InvalidTeamType: If 'home' or 'away' is not supplied
        creation will fail.
    """
    class PeriodStats(UserList):
        """
        Inner Class.

        This class is for easy use to call individual period stats.
        The current implementation is intended to change.

        NOTE:
            Playoff games can have multiple overtimes, which is not captured
            in this class.

        Attributes:
            Unsure lol.
        """
        class Period(object):
            """Inner Class. Used for better accessing period stats."""

            def __init__(self, name, data):
                self.name = name

                parsed_data = parser.period(data)

                for key, val in parsed_data.items():
                    setattr(self, key, val)

            def update_data(self, data):
                parsed_data = parser.period(data)

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

        def __init__(self, periods, team_type):
            self.num_per = len(periods)

            data = []
            for i in range(self.num_per):
                name = periods[i]['ordinalNum']
                data.append(
                    self.Period(name, periods[i][team_type])
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
                    self.data.append(self.Period(name, periods[i][team_type]))

            self.total_shots = sum([x.shots for x in self.data])

        def __repr__(self):
            return f'{self.__class__} -> {self.__dict__}'

    class ShootoutStats(object):
        """Inner Class. Used for better accessing shootout stats."""

        def __init__(self, goals=None, attempts=None):
            self.goals = goals
            self.attempts = attempts

        def __repr__(self):
            return f'{self.__class__} -> {self.__dict__}'

    def __init__(self, game, game_id, team_type, data=None):
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
        if not data:
            # request the game data
            data = request(Url.GAME, url_mods={'game_id': game_id})

        # get the teams id number
        team_id = data['gameData']['teams'][team_type]['id']

        # Call the parent class constructor
        super().__init__(team_id, game.db_conn)

        # holds reference to the Game "container"
        self.game = game
        self.game_id = game_id

        # parse the data
        parsed_data = parser.teams_skater_stats(
            data, self.team_type, True
        )

        # set attributes
        for key, val in parsed_data.items():
            setattr(self, key, val)

        # PeriodStats object for easier referencing
        self.periods = self.PeriodStats(
            data['liveData']['linescore']['periods'], team_type
        )

        # ShootOutStats object for easier referencing
        if data['liveData']['linescore']['hasShootout']:
            self.shootout = self.ShootoutStats(
                goals=data['liveData']['linescore']['shootoutInfo'][team_type]['scores'],  # noqa
                attempts=data['liveData']['linescore']['shootoutInfo'][team_type]['attempts']  # noqa
            )
        else:
            self.shootout = self.ShootoutStats()

        # collect all player ids
        self.id_list = data['liveData']['boxscore']['teams'][team_type]['goalies']  # noqa
        self.id_list.extend(data['liveData']['boxscore']['teams'][team_type]['skaters'])  # noqa
        self.id_list.extend(data['liveData']['boxscore']['teams'][team_type]['scratches'])  # noqa

        # wait to create the actual player objects
        self.players = None

    def init_players(self, data=None):
        """Utility function for explicit control of expensive logic.
        """
        if self.players:
            return

        self.players = PlayerCollection(
            self, self.id_list, GamePlayer
        )

        self.players.create_players(data)

    def update_data(self, data=None):
        """Updates an object using fresh data.

        Args:
            data (dict, optional): JSON API response represented as
                                        a dictionary. Defaults to None.
        """

        if not data:
            data = request(Url.GAME, url_mods={'game_id': game_id})

        _status_code = int(data['gameData']['status']['statusCode'])

        # NOTE: This check could fail if the game status code
        #       is updated before this.
        if _status_code in const.GAME_STATUS['Preview'] and self.game.game_status in const.GAME_STATUS['Preview']:  # noqa
            return

        parsed_data = parser.teams_skater_stats(
            data, self.team_type, True
        )

        for key, val in parsed_data.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise AttributeError(
                    f'Update received an attribute {key} \
                    that has not been set.'
                )

        # we protect against this case in players.update_data
        # but no need to waste computation
        if self.players:
            self.players.update_data(data)

        self.periods.update_data(
            data['liveData']['linescore']['periods'],
            self.team_type
        )

        if data['liveData']['linescore']['hasShootout']:
            self.shootout.goals = data['liveData']['linescore']['shootoutInfo'][team_type]['scores']  # noqa
            self.shootout.attempts = data['liveData']['linescore']['shootoutInfo'][team_type]['attempts']  # noqa

    def top_scorers(self):
        return self.players.top_scorers()


class TeamSeasonStats(BaseTeam):
    """
    Team class for holding a particular season's stats.
    """
    class ValueRank():
        """Helper class for team stats."""

        def __init__(self, name, value, rank=None):
            self.name = name
            self.value = value
            self.rank = rank

        def rank_suffix(self):
            if self.rank is None:
                return None
            elif self.rank % 10 == 1 and (self.rank > 20 or self.rank < 10):
                return str(self.rank) + 'st'
            elif self.rank % 10 == 2 and (self.rank > 20 or self.rank < 10):
                return str(self.rank) + 'nd'
            elif self.rank % 10 == 3 and (self.rank > 20 or self.rank < 10):
                return str(self.rank) + 'rd'
            else:
                return str(self.rank) + 'th'

        def format_value(self):
            prec = get_precision(self.name)

            if prec is None:
                return str(self.value)
            else:
                return '{:.{prec}f}'.format(self.value, prec=prec)

    def __init__(self, team_id, db_conn, stats):
        super().__init__(team_id, db_conn)

        # these are all the team stats returned
        for key, val in stats.items():
            if 'rank' in key:
                # just skip over all rank columns
                continue
            # set an attribute with the name of col, and the value as
            # the ValueRank class
            try:
                setattr(self, key, self.ValueRank(
                    key, val, stats[key + '_rank']
                ))
            except KeyError as keyerr:
                # this is gross. four keys dont have an accompanying rank
                # I think this is faster thought because there is no
                # if statement continuing to run
                setattr(self, key, self.ValueRank(key, val))

    def fetch_splits(self) -> dict:
        """Fetch a teams splits"""
        for stat in self.splits_items():
            if stat.name == 'home_record':
                home = stat.value
            elif stat.name == 'away_record':
                away = stat.value
            elif stat.name == 'last_ten':
                last_ten = stat.value
            else:
                streak = stat.value

        return {
            'home_record': home,
            'away_record': away,
            'last_ten': last_ten,
            'streak': streak
        }

    def all_items(self):
        """Returns iterable of stat"""
        # attributes of BaseTeam that we dont want to return
        base_attrs = [
            'team_id', 'full_name', 'abbreviation',
            'division', 'conference', 'franchise_id'
        ]

        # for all attributes in self
        for i in self.__dict__.keys():
            # if attr in base_attrs
            if i in base_attrs:
                continue
            else:
                yield self.__dict__[i]

    def ranked_items(self):
        """Returns iterable of all stats that have a rank"""
        # attributes of BaseTeam that we dont want to return
        base_attrs = [
            'team_id', 'full_name', 'abbreviation',
            'division', 'conference', 'franchise_id'
        ]

        for i in self.__dict__.keys():
            if i in base_attrs:
                continue
            if self.__dict__[i].rank is None:
                continue
            else:
                yield self.__dict__[i]

    def splits_items(self):
        """Returns iterable of Team splits"""
        # attributes of BaseTeam that we dont want to return
        splits = [
            'home_record', 'away_record', 'streak', 'last_ten'
        ]

        for i in self.__dict__.keys():
            if i in splits:
                yield self.__dict__[i]
