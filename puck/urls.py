from enum import Enum


class Url(Enum):
    '''
    Master List of all possible query targets.
    '''

    TEAMS = 'https://statsapi.web.nhl.com/api/v1/teams/{}'
    SCHEDULE = 'https://statsapi.web.nhl.com/api/v1/schedule'
    TEAM_STATS = 'https://statsapi.web.nhl.com/api/v1/teams/{}/stats'
    RECORDS = 'https://records.nhl.com/site/api'
    GAME = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'
    STANDINGS = 'https://statsapi.web.nhl.com/api/v1/standings'
    PLAYERS = 'https://statsapi.web.nhl.com/api/v1/people/{}'
    PLAYER_STATS = 'https://statsapi.web.nhl.com/api/v1/people/{}/stats'

    @staticmethod
    def appendable():
        '''
        Returns list of Urls that can/require the insertion of IDs or other
        extensions to the url.
        '''

        return [
            Url.TEAMS, Url.TEAM_STATS, Url.RECORDS,
            Url.GAME, Url.STANDINGS, Url.PLAYERS, Url.PLAYER_STATS
        ]