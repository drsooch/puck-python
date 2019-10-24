import puck.games
import unittest


class TestGameCreation(unittest.TestCase):
    def test_game_ids(self):
        # uses an arbitrary day to test
        self.assertListEqual(
            puck.games.Games(
                **{'date': '2019-10-18'}
            ).game_ids,
            [2019020107, 2019020108, 2019020109,
                2019020110, 2019020111, 2019020112]
        )


if __name__ == '__main__':
    unittest.main()
