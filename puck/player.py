from collections import UserList, UserDict
from puck.utils import request
from puck.urls import Url


class BasePlayer(UserDict):
    def __init__(self, player_id, data={}):

        data.update(
            request(Url.PLAYERS, {'player_id': player_id})['people'][0]
        )

        super().__init__(data)

    def update_data(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class GamePlayer(BasePlayer):
    def __init__(self, player_id):
        super().__init__(player_id, initialdata={})


class FullPlayer(BasePlayer):
    def __init__(self, player_id, initialdata={}):
        super().__init__(player_id, initialdata=initialdata)


class PlayerCollection(UserList):
    def __init__(self, initlist=None):
        super().__init__(initlist)


if __name__ == "__main__":
    print(BasePlayer(8470600))
