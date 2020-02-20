from collections import UserDict, UserList

from puck.urls import Url
from puck.utils import request


class BasePlayer(UserDict):
    def __init__(self, db_conn, player_id, data={}):
        self.db_conn = db_conn

        super().__init__(data)

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class GamePlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data={}):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        self.update(data)


class FullPlayer(BasePlayer):
    def __init__(self, db_conn, player_id, data={}):
        super().__init__(db_conn, player_id=player_id, data=data)

    def update_data(self, data):
        self.update(data)


class PlayerCollection(UserList):
    def __init__(self, db_conn, initlist=[], id_list=None, player_type=BasePlayer):  # noqa
        self.db_conn = db_conn
        
        if initlist:
            for i in initlist:
                if not isinstance(i, BasePlayer):
                    raise ValueError(
                        'The initial list provided contained an invalid type, \
                    requires a subclass of BasePlayer'
                    )
        else:
            initlist = [player_type(db_conn, _id) for _id in id_list]

        super().__init__(initlist)


if __name__ == "__main__":
    print(BasePlayer(8470600))
