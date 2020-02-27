from enum import Enum


class URLException(Exception):
    pass


class Url(Enum):
    """
    Master List of all possible Url endpoints.

    """

    TEAMS = 'https://statsapi.web.nhl.com/api/v1/teams/{}'
    TEAM_STATS = 'https://statsapi.web.nhl.com/api/v1/teams/{}/stats'
    TEAM_ROSTER = 'https://statsapi.web.nhl.com/api/v1/teams/{}/roster'
    SCHEDULE = 'https://statsapi.web.nhl.com/api/v1/schedule'
    RECORDS = 'https://records.nhl.com/site/api'
    GAME = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'
    STANDINGS = 'https://statsapi.web.nhl.com/api/v1/standings'
    PLAYERS = 'https://statsapi.web.nhl.com/api/v1/people/{}'
    PLAYER_STATS = 'https://statsapi.web.nhl.com/api/v1/people/{}/stats'

    @staticmethod
    def formattable():
        """
        Returns list of Urls that can/require the insertion of IDs or other
        extensions to the url.

        Returns:
            List of Urls
        """

        return [
            Url.TEAMS, Url.TEAM_STATS, Url.TEAM_ROSTER,
            Url.GAME, Url.PLAYERS, Url.PLAYER_STATS
        ]
