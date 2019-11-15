import unittest

import puck.games
from puck.cli import ISODateType
import click


class PuckCLITest(unittest.TestCase):

    def test_ISODate(self):
        self.assertEqual(
            ISODateType().convert('2011-04-05', None, None), '2011-04-05'
        )
        with self.assertRaises(click.ClickException):
            ISODateType().convert('2011/04/05', None, None)
            ISODateType().convert('42', None, None)


if __name__ == '__main__':
    unittest.main()
