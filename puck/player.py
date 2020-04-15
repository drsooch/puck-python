import asyncio
from collections import UserList

import puck.utils as utils
from puck.urls import Url
from puck.database.db import select_stmt, batch_update_db, execute_constant
import puck.database.db_constants as db_const
from puck.dispatcher import Dispatch
import puck.parser as parser


class BasePlayer(object):
    def __init__(self, db_conn, player_id, parsed_data=None):
        self.db_conn = db_conn
        self.player_id = player_id

        # get info from player_info table
        resp = select_stmt(
            self.db_conn, 'player', db_const.TableColumns.BASE_PLAYER_CLASS,
            where=('player_id', self.player_id)
        )[0]

        # set the attributes from the keys
        for key in resp.keys():
            setattr(self, key, resp[key])

        # data only passed from a child class
        if parsed_data:
            for key, val in parsed_data.items():
                setattr(self, key, val)

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class GamePlayer(BasePlayer):
    def __init__(self, db_conn, player_id, parsed_data):

        super().__init__(db_conn, player_id=player_id, parsed_data=parsed_data)

    def update_data(self, data):
        pd = parser.player_stats_game(data)

        for key, val in pd.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise AttributeError(
                    f'Player Update received an attribute {key} of type \
                    {type(key)} that has not been set. {dir(self)} \
                    ID = {self.player_id}'
                )


class FullPlayer(BasePlayer):
    def __init__(self, db_conn, player_id, parsed_data=None):
        super().__init__(db_conn, player_id=player_id, parsed_data=parsed_data)

    def update_data(self, data):
        pass


class PlayerCollection(object):
    def __init__(self, team, id_list, _class=BasePlayer):
        self.db_conn = team.game.db_conn  # db_conn
        self.team = team    # team object associated with collection
        self.need_to_update = []  # list of players who need to be updated
        self._class = _class      # Player class type
        self.players = []         # Player objs list
        self.forwards = []        # list of indexes that points to self.players
        self.defense = []
        self.goalies = []
        self.not_playing = []

        team_roster = select_stmt(
            self.db_conn, 'player', columns=['player_id'],
            where=('team_id', team.team_id)
        )

        id_set = set(id_list)
        db_set = set()
        for row in team_roster:
            # for each row returned from database check if they are on the team
            player = int(row['player_id'])

            if player not in id_set:
                # this player is no longer on the team or in the AHL
                self.need_to_update.append(player)
            else:
                db_set.add(player)

        # get the difference between id_set and db_set
        # the difference are the players who are definitely on the team
        # but not found in the db
        self.need_to_update.extend(list(id_set - db_set))

        # we just hold reference to the players, takes way too long
        # to populate all games players
        self.player_ids = id_set

    def get_player(self, player_id) -> BasePlayer:
        """Return a player object based on player_id passed"""
        # if we havent created players
        if not self.players:
            self.create_players()

        for player in self.players:
            if player.player_id == player_id:
                return player

        raise KeyError('No player id' + str(player_id))

    def skaters(self):
        """Iterable of skaters in a collection"""
        # combine forwards and defense
        skaters = self.forwards + self.defense
        for skater in skaters:
            yield self.players[skater]

    def goalies(self):
        """Iterable of goalies in Collection"""
        for goalie in self.goalies:
            yield self.players[goalie]

    def create_players(self, data=None):
        """Utility method so we can have control on when to call
        the expensive create logic."""

        if self.players:
            return

        if not data:
            data = utils.request(
                Url.GAME, {'game_id': self.team.game.game_id}
            )

        # cant use isinstance of.
        if self._class == GamePlayer:
            data_copy = data['liveData']['boxscore']['teams'][self.team.team_type]['players']  # noqa
        else:
            data_copy = data

        # this should always hit
        # unless no changes were deemed necessary at init
        if self.need_to_update:
            self.replace_players()

        index = 0
        for player in self.player_ids:
            # strip off the ID part
            player_data = data_copy['ID' + str(player)]

            # parse and create player
            pd = parser.player_stats_game(player_data)
            player_obj = self._class(self.db_conn, player, pd)

            # if a player is scratched parser returns None
            if pd is not None:
                # keep index pointers for each player object in self.players
                if player_obj.position == 'G':
                    self.goalies.append(index)
                elif player_obj.position == 'D':
                    self.defense.append(index)
                else:
                    self.forwards.append(index)
            else:
                self.not_playing.append(index)

            # increment index and add the player_obj
            index += 1
            self.players.append(player_obj)

    def top_scorers(self):
        ts = execute_constant(
            self.db_conn,
            db_const.TOP_SCORER_TEAM.format(
                self.team.team_id, utils.get_season_number(
                    self.team.game.game_date
                )
            )
        )

        for player in ts:
            if player['goals_rank'] == 1:
                goals = {
                    'value': player['goals'],
                    'id': player['player_id']
                }

            if player['assists_rank'] == 1:
                assists = {
                    'value': player['assists'],
                    'id': player['player_id']
                }

            if player['points_rank'] == 1:
                points = {
                    'value': player['points'],
                    'id': player['player_id']
                }

        return {
            'goals': goals,
            'assists': assists,
            'points': points
        }

    def update_data(self, data):

        if self._class == GamePlayer:
            data_copy = data['liveData']['boxscore']['teams'][self.team.team_type]['players']  # noqa
        else:
            data_copy = data

        # this should never be true but just in case
        if self.need_to_update:
            self.replace_players()

        # basically a noop if players is empty list.
        if self.players:
            for player in self.players:
                player_data = data_copy['ID' + str(player.player_id)]
                player.update_data(player_data)

    def replace_players(self):
        """
        Since we cannot effectively update players in an async loop
        Have a designated function to do so. This should be called as soon
        as possible.
        """
        if not self.need_to_update:
            return

        # update the database
        asyncio.run(
            batch_update_db(
                self.need_to_update, self.db_conn,
                Dispatch.player_info
            )
        )
        self.need_to_update = []
