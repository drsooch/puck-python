"""
Dispatcher class is used to allow for ease of passing certain keyword strings.

Designed to simplify the batch functions.
"""
import puck.parser as p
from puck.urls import Url


class Dispatch(object):
    def __init__(self, _id, id_type, name=None, parser=None, table=None, url=None, params=None):  # noqa
        self.id = _id
        self.id_type = id_type

        if name is None and parser is not None:
            self.name = parser
        else:
            self.name = name

        self.parser = p.get_parser(parser)
        self.table = table
        self.url = url
        self.params = params

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'

    @classmethod
    def player_info(cls, _id):
        return Dispatch(
            _id, 'player_id', parser='player_info',
            table='player', url=Url.PLAYERS
        )

    @classmethod
    def skater_stats(cls, _id):
        return Dispatch(
            _id, 'player_id', parser='skater_season_stats',
            table='skater_season_stats', url=Url.PLAYER_STATS_ALL
        )

    @classmethod
    def goalie_stats(cls, _id):
        return Dispatch(
            _id, 'player_id', parser='goalie_season_stats',
            table='goalie_season_stats', url=Url.PLAYER_STATS_ALL
        )

    @classmethod
    def game(cls, _id):
        return Dispatch(_id, 'game_id', parser='game', url=Url.GAME)

    @classmethod
    def team_info(cls, _id):
        return Dispatch(
            _id, 'team_id', parser='team_info',
            table='team', url=Url.TEAMS
        )

    @classmethod
    def team_season(cls, _id, season):
        return Dispatch(
            _id, 'team_id', parser='team_season_stats', table='team_season',
            url=Url.TEAMS, params={'expand': 'team.stats', 'season': (season)}
        )

    @classmethod
    def roster(cls, _id):
        return Dispatch(_id, 'team_id', parser='roster', url=Url.TEAM_ROSTER)

    @classmethod
    def empty(cls, name=None):
        return Dispatch(None, None, name=name)
