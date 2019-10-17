import puck.puck.utils as utils
import unittest

class TestUtils(unittest.TestCase):
    def get_test(self):
        with self.assertRaises():
            utils._get_url(utils._SCHEDULE_URL, params={"BadParam": "1"})

if __name__ == "__main__":
    unittest.main()