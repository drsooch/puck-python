"""
Dispatcher class is used to allow for ease of passing certain keyword strings.

Designed to simplify the batch functions.
"""
import puck.parser as p
from puck.urls import Url


class Dispatch(object):
    def __init__(self, id_type, parser=None, table=None, url=None):
        self.id_type = id_type
        self.parser = p.get_parser(parser)
        self.table = table
        self.url = url

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'

    @classmethod
    def player_info(cls):
        return Dispatch('player_id', 'player_info', 'player', Url.PLAYERS)

    @classmethod
    def game(cls):
        return Dispatch('game_id', 'game', url=Url.GAME)

    @classmethod
    def team_info(cls):
        return Dispatch('team_id', 'team_info', 'team', Url.TEAMS)
