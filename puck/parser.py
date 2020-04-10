"""
Main parsing logic for reading JSON objects. Covers all types of data: Players,
Player Stats, Teams, Team Stats, Games, Games Stats etc.

All functions return a dictionary of with cleaned up normalized keys.
"""

from collections import defaultdict

import arrow

import puck.constants as const


class InvalidParserException(Exception):
    pass


def game(data) -> defaultdict:
    """
    Parses Url.GAME JSON data. Returns a dictionary of the necessary
    values to create both a Banner and Full Game.

    Url.GAME

    Args:
        data (json): Url.Game endpoint json object

    Returns:
        dict: Dictionary of attribute values for the games class
    """
    parsed_data = defaultdict(lambda: None)
    game_data = data['gameData']
    linescore = data['liveData']['linescore']

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


def period(data) -> defaultdict:
    """Parse a single periods data

    Url.GAME

    Args:
        data (dict): dict representing a JSON object of a single period

    Returns:
        defaultdict: Parsed Data.
    """
    parsed_data = defaultdict(lambda: None)

    parsed_data['goals'] = data['goals']
    parsed_data['shots'] = data['shotsOnGoal']

    return parsed_data


def player_info(data) -> defaultdict:
    """Parse generic player info, also providing mapping to database columns.

    Url.PLAYERS

    Args:
        data (dict): dict representing a JSON object for player info.

    Returns:
        defaultdict: Parsed Data.
    """
    data_copy = data['people'][0]

    parsed_data = defaultdict(lambda: None)

    parsed_data['player_id'] = data_copy['id']
    parsed_data['team_id'] = data_copy['currentTeam']['id']
    parsed_data['first_name'] = data_copy['firstName']
    parsed_data['last_name'] = data_copy['lastName']
    parsed_data['number'] = data_copy.get('primaryNumber', None)
    parsed_data['position'] = data_copy['primaryPosition']['abbreviation']
    parsed_data['handedness'] = data_copy['shootsCatches']
    parsed_data['rookie'] = data_copy['rookie']
    parsed_data['age'] = data_copy['currentAge']
    parsed_data['birth_date'] = data_copy['birthDate']
    parsed_data['birth_city'] = data_copy['birthCity']
    parsed_data['birth_state'] = data_copy.get('birthStateProvince', None)
    parsed_data['birth_country'] = data_copy['birthCountry']
    parsed_data['height'] = data_copy['height']
    parsed_data['weight'] = data_copy['weight']

    return parsed_data


def team_info(data) -> defaultdict:
    """Parse generic team info, provides mapping to database

    Url.TEAMS

    Args:
        data (dict): dict representing JSON object of basic team info.

    Returns:
        defaultdict: Parsed Data.
    """
    data_copy = data['teams'][0]

    parsed_data = defaultdict(lambda: None)

    parsed_data['team_id'] = data_copy['id']
    parsed_data['full_name'] = data_copy['name']
    parsed_data['abbreviation'] = data_copy['abbreviation']
    parsed_data['division'] = data_copy['division']['id']
    parsed_data['conference'] = data_copy['conference']['id']
    parsed_data['active'] = data_copy['active']
    parsed_data['franchise_id'] = data_copy['franchiseId']

    # this must be hardcoded here only data from NHL teams will be
    # passed to this parser
    parsed_data['league_id'] = 133

    return parsed_data


def teams_skater_stats(data, team_type, full_team=False) -> defaultdict:
    """Parser for a teams skater stats for one game.
    Receives the full JSON representation.

    Url.GAME

    Args:
        data (dict): dict representing JSON object of skater stats
        team_type (str): Either home or away
        full_team (bool, optional): If caller is a FullStatsTeam class.
                                   Defaults to False.

    Returns:
        defaultdict: Parsed Data.
    """
    data_copy = data['liveData']['boxscore']['teams'][team_type]['teamStats']['teamSkaterStats']  # noqa

    parsed_data = defaultdict(lambda: None)

    parsed_data['goals'] = data_copy['goals']

    if full_team:
        parsed_data['pims'] = data_copy['pim']
        parsed_data['shots'] = data_copy['shots']
        parsed_data['pp_pct'] = data_copy['powerPlayPercentage']
        parsed_data['pp_goals'] = data_copy['powerPlayGoals']
        parsed_data['pp_att'] = data_copy['powerPlayOpportunities']
        parsed_data['faceoff_pct'] = data_copy['faceOffWinPercentage']
        parsed_data['blocked'] = data_copy['blocked']
        parsed_data['takeaways'] = data_copy['takeaways']
        parsed_data['giveaways'] = data_copy['giveaways']
        parsed_data['hits'] = data_copy['hits']

    return parsed_data


def player_stats_game(data) -> defaultdict:
    """Individual Game stat parser. Directs parsing to the proper
    player parser (goalie or skater).

    Receives the player_id branch.

    Url.GAME

    Args:
        data (dict): dict representing JSON object.

    Returns:
        defaultdict: Parsed Data.
    """
    # if the stats dict is empty it means they're scratched
    if not data['stats']:
        return None

    if data['position']['abbreviation'] == 'G':
        return goalie_stats_game(data['stats']['goalieStats'])
    else:
        return skater_stats_game(data['stats']['skaterStats'])


def goalie_stats_game(data) -> defaultdict:
    """Goalie stats parser for individual games.
    Provides key mapping to database.

    Receives goalieStats branch.

    Url.GAME

    Args:
        data (dict): dict representing JSON object.
    """

    parsed_data = defaultdict(lambda: None)

    parsed_data['time_on_ice'] = data['timeOnIce']
    parsed_data['assists'] = data['assists']
    parsed_data['goals'] = data['goals']
    parsed_data['pims'] = data['pim']
    parsed_data['shots_against'] = data['shots']
    parsed_data['saves'] = data['saves']
    parsed_data['pp_saves'] = data['powerPlaySaves']
    parsed_data['sh_saves'] = data['shortHandedSaves']
    parsed_data['ev_saves'] = data['evenSaves']
    parsed_data['sh_shots'] = data['shortHandedShotsAgainst']
    parsed_data['ev_shots'] = data['evenShotsAgainst']
    parsed_data['pp_shots'] = data['powerPlayShotsAgainst']

    # if game isn't finished
    parsed_data['decision'] = data.get('decision', None)

    # if the game hasn't started or goalie hasn't played
    parsed_data['save_pct'] = data.get('savePercentage', 0)
    parsed_data['pp_save_pct'] = data.get('powerPlaySavePercentage', 0)
    parsed_data['sh_save_pct'] = data.get('shortHandedSavePercentage', 0)
    parsed_data['ev_save_pct'] = data.get('evenStrengthSavePercentage', 0)

    return parsed_data


def skater_stats_game(data) -> defaultdict:
    """Skater's game stats parser.
    Provides database key mapping.

    Receives skaterStats branch.

    Url.GAME

    Args:
        data (dict): dict representing JSON object.

    Returns:
        defaultdict: Parsed Data.
    """
    parsed_data = defaultdict(lambda: None)

    parsed_data['time_on_ice'] = data['timeOnIce']
    parsed_data['assists'] = data['assists']
    parsed_data['goals'] = data['goals']
    parsed_data['pims'] = data['penaltyMinutes']
    parsed_data['shots'] = data['shots']
    parsed_data['hits'] = data['hits']
    parsed_data['pp_goals'] = data['powerPlayGoals']
    parsed_data['sh_goals'] = data['shortHandedGoals']
    parsed_data['ev_goals'] = parsed_data['goals'] - \
        parsed_data['pp_goals'] - parsed_data['sh_goals']
    parsed_data['pp_assists'] = data['powerPlayAssists']
    parsed_data['sh_assists'] = data['shortHandedAssists']
    parsed_data['ev_assists'] = parsed_data['assists'] - \
        parsed_data['pp_assists'] - parsed_data['sh_assists']

    # if the player is not a forward, they don't get this key.
    parsed_data['faceoff_pct'] = data.get('faceOffPct', 0)
    parsed_data['faceoff_wins'] = data['faceOffWins']
    parsed_data['faceoff_taken'] = data['faceoffTaken']
    parsed_data['takeaways'] = data['takeaways']
    parsed_data['giveaways'] = data['giveaways']
    parsed_data['blocked'] = data['blocked']
    parsed_data['plus_minus'] = data['plusMinus']
    parsed_data['ev_toi'] = data['evenTimeOnIce']
    parsed_data['pp_toi'] = data['powerPlayTimeOnIce']
    parsed_data['sh_toi'] = data['shortHandedTimeOnIce']

    return parsed_data


def team_season_stats(data, metadata=False, season=None) -> defaultdict:
    """Parse a teams single season stats. Provides a database mapping.

    Url.TEAMS ?expand=team.stats&season=NUM

    Args:
        data (dict): dict representing JSON object of a team's season stats
        metadata (bool, optional): If season meta data is needed.
                                  Defaults to False.
        season (str or int, optional): Season identifier i.e. 20172018 etc.
                                      Defaults to None.

    Returns:
        defaultdict: Parsed Data
    """
    data_copy = data['teams'][0]
    parsed_data = defaultdict(lambda: None)

    # if we need to post to team season table first
    if metadata:
        parsed_data['team_season'] = defaultdict(lambda: None)
        parsed_data['team_season']['team_id'] = data_copy['id']
        parsed_data['team_season']['season'] = season
        parsed_data['team_season']['franchise_id'] = data_copy['franchise']['franchiseId']  # noqa
        parsed_data['team_season']['division_id'] = data_copy['division']['id']
        parsed_data['team_season']['conference_id'] = data_copy['conference']['id']  # noqa

    # shorten JSON tree
    data_copy = data['teams'][0]['teamStats'][0]['splits'][0]['stat']

    parsed_data['games_played'] = data_copy['gamesPlayed']
    parsed_data['wins'] = data_copy['wins']
    parsed_data['losses'] = data_copy['losses']
    parsed_data['ot_losses'] = data_copy['ot']
    parsed_data['points'] = data_copy['pts']
    parsed_data['pt_pct'] = data_copy['ptPctg']
    parsed_data['goals_for_pg'] = data_copy['goalsPerGame']
    parsed_data['goals_ag_pg'] = data_copy['goalsAgainstPerGame']
    parsed_data['evgga_ratio'] = data_copy['evGGARatio']
    parsed_data['pp_pct'] = data_copy['powerPlayPercentage']
    parsed_data['pp_goals_for'] = data_copy['powerPlayGoals']
    parsed_data['pp_goals_ag'] = data_copy['powerPlayGoalsAgainst']
    parsed_data['pp_opp'] = data_copy['powerPlayOpportunities']
    parsed_data['pk_pct'] = data_copy['penaltyKillPercentage']
    parsed_data['shots_for_pg'] = data_copy['shotsPerGame']
    parsed_data['shots_ag_pg'] = data_copy['shotsAllowed']
    parsed_data['win_score_first'] = data_copy['winScoreFirst']
    parsed_data['win_opp_score_first'] = data_copy['winOppScoreFirst']
    parsed_data['win_lead_first_per'] = data_copy['winLeadFirstPer']
    parsed_data['win_lead_second_per'] = data_copy['winLeadSecondPer']
    parsed_data['win_outshoot_opp'] = data_copy['winOutshootOpp']
    parsed_data['win_outshot_by_opp'] = data_copy['winLeadFirstPer']
    parsed_data['faceoffs_taken'] = data_copy['faceOffsTaken']
    parsed_data['faceoff_wins'] = data_copy['faceOffsWon']
    parsed_data['faceoff_losses'] = data_copy['faceOffsLost']
    parsed_data['faceoff_pct'] = data_copy['faceOffWinPercentage']
    parsed_data['shooting_pct'] = data_copy['shootingPctg']
    parsed_data['save_pct'] = data_copy['savePctg']

    # unfortunately the JSON for the above parsing does not have
    # regulation Wins included
    # As of April 5th 2020, this function only adds regulation wins
    # it may be expanded in the future
    team_standings_stats(
        parsed_data['team_season']['team_id'],
        parsed_data['team_season']['division_id'],
        parsed_data['team_season']['season'],
        parsed_data
    )

    return parsed_data


def team_standings_stats(team_id, division, season, parsed_data):
    """Queries the Standings endpoint for Regulation Wins"""
    from puck.utils import get_season_number

    if season != get_season_number():
        return

    from puck.utils import request
    from puck.urls import Url

    data = request(Url.STANDINGS, {'team_id': team_id}, {'season': (season)})

    # maps division to an index that Url.Standings returns
    divisions = {
        18: 0,
        17: 1,
        16: 2,
        15: 3
    }
    data = data['records'][divisions[division]]['teamRecords']

    for i in data:
        if i['team']['id'] == team_id:
            # we only need this one column :(
            parsed_data['reg_wins'] = i['row']
            break


def roster(data) -> list:
    """Simple parser to get all players on a roster.

    Url.ROSTER

    Args:
        data (dict): dict representing JSON object of a team's roster

    Returns:
        list: list of player ids
    """
    parsed_data = []
    for person in data['roster']:
        parsed_data.append(person['person']['id'])

    return parsed_data


def skater_season_stats(data) -> defaultdict:
    """Parser for a skater's season stats. Provides database mapping.

    Url.PLAYER_STATS_ALL

    Args:
        data (dict): dict representing JSON object of a skaters
                      full season stats

    Returns:
        defaultdict: Parsed Data
    """
    parsed_data = defaultdict(lambda: None)

    metadata_players(data, parsed_data)

    parsed_data['time_on_ice'] = data['stat'].get('timeOnIce', None)
    parsed_data['assists'] = data['stat'].get('assists', None)
    parsed_data['goals'] = data['stat'].get('goals', None)
    parsed_data['points'] = data['stat'].get('points', None)
    parsed_data['pims'] = data['stat'].get('pim', None)
    parsed_data['shots'] = data['stat'].get('shots', None)
    parsed_data['games'] = data['stat'].get('games', None)
    parsed_data['hits'] = data['stat'].get('hits', None)
    parsed_data['pp_goals'] = data['stat'].get('powerPlayGoals', None)
    parsed_data['pp_points'] = data['stat'].get('powerPlayPoints', None)
    parsed_data['pp_toi'] = data['stat'].get('powerPlayTimeOnIce', None)
    parsed_data['sh_goals'] = data['stat'].get('shortHandedGoals', None)
    parsed_data['sh_points'] = data['stat'].get('shortHandedPoints', None)
    parsed_data['sh_toi'] = data['stat'].get('shortHandedTimeOnIce', None)
    parsed_data['ev_toi'] = data['stat'].get('evenTimeOnIce', None)
    parsed_data['faceoff_pct'] = data['stat'].get('faceOffPct', None)
    parsed_data['shooting_pct'] = data['stat'].get('shotPct', None)
    parsed_data['gwg'] = data['stat'].get('gameWinningGoals', None)
    parsed_data['ot_goals'] = data['stat'].get('overTimeGoals', None)
    parsed_data['plus_minus'] = data['stat'].get('plusMinus', None)
    parsed_data['blocked'] = data['stat'].get('blocked', None)
    parsed_data['shifts'] = data['stat'].get('shifts', None)

    return parsed_data


def goalie_season_stats(data) -> defaultdict:
    """Parser for a goalie's season stats. Provides database mapping.

    Url.PLAYER_STATS_ALL

    Args:
        data (dict): dict representing JSON object of a goalie's
                      full season stats

    Returns:
        defaultdict: Parsed Data
    """

    parsed_data = defaultdict(lambda: None)

    metadata_players(data, parsed_data)

    parsed_data['games'] = data['stat'].get('games', None)
    parsed_data['save_pct'] = data['stat'].get('savePercentage', None)
    parsed_data['gaa'] = data['stat'].get('goalAgainstAverage', None)
    parsed_data['ot_losses'] = data['stat'].get('ot', None)
    parsed_data['shutouts'] = data['stat'].get('shutouts', None)
    parsed_data['wins'] = data['stat'].get('wins', None)
    parsed_data['ties'] = data['stat'].get('ties', None)
    parsed_data['losses'] = data['stat'].get('losses', None)
    parsed_data['saves'] = data['stat'].get('saves', None)
    parsed_data['pp_saves'] = data['stat'].get('powerPlaySaves', None)
    parsed_data['sh_saves'] = data['stat'].get('shortHandedSaves', None)
    parsed_data['ev_saves'] = data['stat'].get('evenSaves', None)
    parsed_data['pp_shots'] = data['stat'].get('powerPlayShots', None)
    parsed_data['sh_shots'] = data['stat'].get('shortHandedShots', None)
    parsed_data['ev_shots'] = data['stat'].get('evenShots', None)
    parsed_data['games_started'] = data['stat'].get('gamesStarted', None)
    parsed_data['shots_against'] = data['stat'].get('shotsAgainst', None)
    parsed_data['goals_against'] = data['stat'].get('goalsAgainst', None)
    parsed_data['pp_save_pct'] = data['stat'].get(
        'powerPlaySavePercentage', None)
    parsed_data['sh_save_pct'] = data['stat'].get(
        'shortHandedSavePercentage', None)
    parsed_data['ev_save_pct'] = data['stat'].get(
        'evenStrengthSavePercentage', None)

    return parsed_data


def _season_info(data, parsed_data):
    """Metadata of a season. Utilized by skater/goalie season stats."""
    # goes into player_season table
    parsed_data['season_data'] = defaultdict(lambda: None)
    parsed_data['season_data']['league_id'] = data['league'].get('id', None)
    parsed_data['season_data']['league_name'] = data['league']['name']
    parsed_data['season_data']['team_id'] = data['team'].get('id', None)
    parsed_data['season_data']['team_name'] = data['team']['name']
    parsed_data['season_data']['season'] = data['season']


def _team_info(data, parsed_data):
    """Metadata of a players Season - Team info."""
    parsed_data['team_data'] = defaultdict(lambda: None)
    parsed_data['team_data']['full_name'] = data['team'].get('name')

    # most team names have no id, simple hash for the id
    team_id_hash = sum([ord(x) for x in parsed_data['team_data']['full_name']])
    team_id_hash = team_id_hash + (team_id_hash % len(parsed_data['team_data']['full_name']))  # noqa

    parsed_data['team_data']['team_id'] = data['team'].get('id', team_id_hash)
    parsed_data['team_data']['league_id'] = data['league'].get('id', None)

    # if this is a non NHL team add the hash to season metadata
    if parsed_data['season_data']['team_id'] is None:
        parsed_data['season_data']['team_id'] = team_id_hash


def _league_info(data, parsed_data):
    """Metadata of a players season - League Info."""
    parsed_data['league_data'] = defaultdict(lambda: None)
    parsed_data['league_data']['league_name'] = data['league']['name']

    league_id_hash = sum(
        [ord(x) for x in parsed_data['league_data']['league_name']]
    )
    league_id_hash = league_id_hash + (league_id_hash % len(parsed_data['league_data']['league_name']))  # noqa

    parsed_data['league_data']['league_id'] = data['league'].get(
        'id', league_id_hash
    )

    # if this is a non NHL team add the hash to season metadata
    if parsed_data['season_data']['league_id'] is None:
        parsed_data['season_data']['league_id'] = league_id_hash

    # add hash to team metadata
    if parsed_data['team_data']['league_id'] is None:
        parsed_data['team_data']['league_id'] = league_id_hash


def metadata_players(data, parsed_data):
    """Wrapper around these three functions.
    They must be in SEASON -> TEAM -> LEAGUE order"""
    _season_info(data, parsed_data)
    _team_info(data, parsed_data)
    _league_info(data, parsed_data)


def invalid_parser(*args, **kwargs):
    raise InvalidParserException('Cannot call an Invalid Parser.')


def get_parser(parser_type):
    """Returns a parser based on key passed. Used in the Dispatch class.

    Args:
        parser_type (string): parser name.

    Returns:
        function: The parser function.
    """
    if parser_type is None:
        # Certain Dispatchers use None type as a parser aka They don't need one
        # Just have a function to raise an error if this parser is called.
        # produces a better error message than None Type is not callable
        return invalid_parser

    parser_handler = {
        'game': game,
        'player_info': player_info,
        'skater_season_stats': skater_season_stats,
        'goalie_season_stats': goalie_season_stats,
        'team_info': team_info,
        'team_season_stats': team_season_stats,
        'team_skater_stats': teams_skater_stats,
        'roster': roster
    }

    return parser_handler[parser_type]
