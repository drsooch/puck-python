import asyncio
from collections import UserList

from puck.database.db import select_stmt, batch_update_db
from puck.dispatcher import Dispatch


class BasePlayer(object):
    def __init__(self, db_conn, player_id, data={}):
        self.db_conn = db_conn

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class GamePlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data={}):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        pass


class FullPlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data={}):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        pass


class PlayerCollection(UserList):
    def __init__(self, team, db_conn, id_list, _class=BasePlayer):  # noqa
        self.db_conn = db_conn
        self.team = team

        team_roster = select_stmt(
            db_conn, 'player', columns=['player_id'],
            where=('team_id', team.team_id)
        )

        # complex logic for a simple task
        # use set mathematics to find out the players who need to be updated
        id_set = set(id_list)
        db_set = set()
        update_list = []
        for row in team_roster:
            # for each row returned from database check if they are on the team
            player = int(row['player_id'])

            if player not in id_list:
                # this player is no longer on the team
                update_list.append(player)
            else:
                db_set.add(player)

        # get the difference between id_set and db_set
        # the difference are the players who are definitely on the team
        # but not found in the db
        update_list.append(list(id_set - db_set))

        # asyncio.run(batch_player_update(update_list))

        # initlist = [_class(db_conn, player_id) for player_id in id_list]

        super().__init__([])


if __name__ == "__main__":
    print(BasePlayer(8470600))
