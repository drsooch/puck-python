import puck.utils as utils
from puck.urls import Url
import unittest


class TestUtils(unittest.TestCase):
    def get_test(self):
        with self.assertRaises():
            utils.get_url(Url.GAME, params={"BadParam": "1"})


if __name__ == "__main__":
    unittest.main()
