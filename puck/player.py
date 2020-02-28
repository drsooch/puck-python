import asyncio
from collections import UserList

from puck.utils import request
from puck.database.db import select_stmt, batch_update_db
from puck.dispatcher import Dispatch


class BasePlayer(object):
    def __init__(self, db_conn, player_id, data=None):
        self.db_conn = db_conn
        self.player_id = player_id

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class GamePlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data=None):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        pass


class FullPlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data=None):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        pass


class PlayerCollection(object):
    def __init__(self, team, id_list, _class=BasePlayer):  # noqa
        self.db_conn = team.game.db_conn
        self.team = team
        self.need_to_update = []
        self._class = _class
        self.players_created = False

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
        self.player_list = id_set

    def update_data(self):
        pass

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
                Dispatch.player_info()
            )
        )

        if self.players_created:
            new_players = []
            for player in self.player_list:
                if player.player_id in self.need_to_update:
                    index = self.player_list.index(player)
                    # get the index and id number of the player to update
                    new_players.append((index, player.player_id))

            for new_p in new_players:
                self.player_list[new_p[0]] = self._class(
                    self.db_conn, new_p[1])

        self.need_to_update = []
