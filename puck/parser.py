"""
Main parsing logic for reading JSON objects. Covers all types of data: Players,
Player Stats, Teams, Team Stats, Games, Games Stats etc.

All functions return a dictionary of with cleaned up normalized keys.
"""

from collections import defaultdict

import arrow

import puck.constants as const

def game_parser(game_info) -> dict:
    """
    Parses Url.GAME JSON data. Returns a dictionary of the necessary
    values to create both a Banner and Full Game.

    Args:
        game_info (json): Url.Game endpoint json object

    Returns:
        dict: Dictionary of attribute values for the games class
    """
    parsed_data = defaultdict(lambda: None)
    game_data = game_info['gameData']
    linescore = game_info['liveData']['linescore']

    parsed_data['game_status'] = int(game_data['status']['statusCode'])
    parsed_data['start_time'] = arrow.get(
        game_data['datetime']['dateTime']
    ).to('local').strftime('%I:%M %p %Z')
    parsed_data['game_date'] = arrow.get(
        game_data['datetime']['dateTime']
    ).to('local').date()

    if parsed_data['game_status'] in const.GAME_STATUS['Preview']:
        parsed_data['period'] = None
        parsed_data['time'] = None
        parsed_data['in_intermission'] = False
        parsed_data['is_live'] = False
        parsed_data['is_final'] = False
        parsed_data['is_preview'] = True
    else:
        parsed_data['period'] = linescore['currentPeriodOrdinal']
        parsed_data['time'] = linescore['currentPeriodTimeRemaining']
        parsed_data['in_intermission'] = linescore['intermissionInfo']['inIntermission']  # noqa
        parsed_data['is_preview'] = None

        if parsed_data['game_status'] in const.GAME_STATUS['Final']:
            parsed_data['is_final'] = True
            parsed_data['is_live'] = False
        else:
            parsed_data['is_final'] = False
            parsed_data['is_live'] = True

    return parsed_data


def teams_skater_stats_parser(team_data, team_type, full_team) -> dict:
    team_data = team_data['liveData']['boxscore']['teams'][team_type]['teamStats']['teamSkaterStats']  # noqa

    parsed_data = defaultdict(lambda: None)

    parsed_data['goals'] = team_data['goals']

    if full_team:
        parsed_data['pims'] = team_data['pim']
        parsed_data['shots'] = team_data['shots']
        parsed_data['pp_pct'] = team_data['powerPlayPercentage']
        parsed_data['pp_goals'] = team_data['powerPlayGoals']
        parsed_data['pp_att'] = team_data['powerPlayOpportunities']
        parsed_data['faceoff_pct'] = team_data['faceOffWinPercentage']
        parsed_data['blocked'] = team_data['blocked']
        parsed_data['takeaways'] = team_data['takeaways']
        parsed_data['giveaways'] = team_data['giveaways']
        parsed_data['hits'] = team_data['hits']

    return parsed_data


def period_parser(period_data) -> dict:
    parsed_data = defaultdict(lambda: None)

    parsed_data['goals'] = period_data['goals']
    parsed_data['shots'] = period_data['shotsOnGoal']

    return parsed_data


def player_info_parser(player_data) -> dict:
    player_data = player_data['people'][0]

    parsed_data = defaultdict(lambda: None)

    parsed_data['player_id'] = player_data['id']
    parsed_data['team_id'] = player_data['currentTeam']['id']
    parsed_data['first_name'] = player_data['firstName']
    parsed_data['last_name'] = player_data['lastName']
    parsed_data['number'] = player_data.get('primaryNumber', None)
    parsed_data['position'] = player_data['primaryPosition']['abbreviation']
    parsed_data['handedness'] = player_data['shootsCatches']
    parsed_data['rookie'] = player_data['rookie']
    parsed_data['age'] = player_data['currentAge']
    parsed_data['birth_date'] = player_data['birthDate']
    parsed_data['birth_city'] = player_data['birthCity']
    parsed_data['birth_state'] = player_data.get('birthStateProvince', None)
    parsed_data['birth_country'] = player_data['birthCountry']
    parsed_data['height'] = player_data['height']
    parsed_data['weight'] = player_data['weight']

    return parsed_data


def team_info_parser(team_data) -> dict:
    team_data = team_data['teams'][0]

    parsed_data = defaultdict(lambda: None)

    parsed_data['team_id'] = team_data['id']
    parsed_data['full_name'] = team_data['name']
    parsed_data['abbreviation'] = team_data['abbreviation']
    parsed_data['division'] = team_data['division']['id']
    parsed_data['conference'] = team_data['conference']['id']
    parsed_data['active'] = team_data['active']
    parsed_data['franchise_id'] = team_data['franchiseId']

    return parsed_data


def get_parser(parser_type):
    parser_handler = {
        'game': game_parser,
        'team_skater_stats': teams_skater_stats_parser,
        'team_info': team_info_parser,
        'player_info': player_info_parser,
    }

    return parser_handler(parser_type)
