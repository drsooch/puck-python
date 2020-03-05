import asyncio
from collections import UserList

from puck.utils import request
from puck.urls import Url
from puck.database.db import select_stmt, batch_update_db
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
        )

        try:
            resp = resp[0]
        except Exception as exc:
            print(player_id)
            print(exc)
            print(dir(resp))
            print(resp)
            while True:
                pass

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
                    f'Player Update received an attribute {key} \
                    that has not been set.'
                )


class FullPlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data=None):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        pass


class PlayerCollection(object):
    def __init__(self, team, id_list, _class=BasePlayer):
        self.db_conn = team.game.db_conn
        self.team = team
        self.need_to_update = []
        self._class = _class
        self.players_created = False
        self.players = []

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
                # this player is no longer on the team
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

    def create_players(self, data=None):
        """Utility method so we can have control on when to call
        the expensive create logic."""

        if self.players_created:
            return

        if not data:
            data = request(
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

        for player in self.player_ids:
            player_data = data_copy['ID' + str(player)]
            pd = parser.player_stats_game(player_data)

            # if a player is scratched parser returns None
            if pd is not None:
                self.players.append(
                    self._class(self.db_conn, player, player_data)
                )

    def update_data(self, data):

        if self._class == GamePlayer:
            data_copy = data['liveData']['boxscore']['teams'][self.team.team_type]['players']  # noqa
        else:
            data_copy = data

        # this should never be true but just in case
        if self.need_to_update:
            self.replace_players()

        # basically a noop if false.
        if self.players_created:
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
