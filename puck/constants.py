GAME_STATUS = {
    'Preview': [1, 2, 8, 9],
    'Final': [5, 6, 7],
    'Live': [3, 4]
}

GAME_D_STATUS = {
    'Preview': 1,
    'Pre-Game': 2,
    'Live': [3, 4],
    'Final': [6, 7]
}

# mapping for short name to ID
TEAM_ID = {
    'NJD': 1, 'NYI': 2, 'NYR': 3, 'PHI': 4,
    'PIT': 5, 'BOS': 6, 'BUF': 7, 'MTL': 8,
    'OTT': 9, 'TOR': 10, 'CAR': 12, 'FLA': 13,
    'TBL': 14, 'WSH': 15, 'CHI': 16, 'DET': 17,
    'NSH': 18, 'STL': 19, 'CGY': 20, 'COL': 21,
    'EDM': 22, 'VAN': 23, 'ANA': 24, 'DAL': 25,
    'LAK': 26, 'SJS': 28, 'CBJ': 29, 'MIN': 30,
    'WPG': 52, 'ARI': 53, 'VGK': 54
}

# this is my worst creation. SELECTS from the DB can return 31 teams
# in certain cases. With this mapping you can directly index into the response.
TEAM_INDEX = {
    1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9,
    12: 10, 13: 11, 14: 12, 15: 13, 16: 14, 17: 15, 18: 16, 19: 17,
    20: 18, 21: 19, 22: 20, 23: 21, 24: 22, 25: 23, 26: 24, 28: 25,
    29: 26, 30: 27, 52: 28, 53: 29, 54: 30
}


# Short name into full
TEAM_SL = {
    'NJD': 'New Jersey Devils', 'NYI': 'New York Islanders',
    'NYR': 'New York Rangers', 'PHI': 'Philadelphia Flyers',
    'PIT': 'Pittsburgh Penguins', 'BOS': 'Boston Bruins',
    'BUF': 'Buffalo Sabres', 'MTL': 'Montréal Canadiens',
    'OTT': 'Ottawa Senators', 'TOR': 'Toronto Maple Leafs',
    'CAR': 'Carolina Hurricanes', 'FLA': 'Florida Panthers',
    'TBL': 'Tampa Bay Lightning', 'WSH': 'Washington Capitals',
    'CHI': 'Chicago Blackhawks', 'DET': 'Detroit Red Wings',
    'NSH': 'Nashville Predators', 'STL': 'St. Louis Blues',
    'CGY': 'Calgary Flames', 'COL': 'Colorado Avalanche',
    'EDM': 'Edmonton Oilers', 'VAN': 'Vancouver Canucks',
    'ANA': 'Anaheim Ducks', 'DAL': 'Dallas Stars',
    'LAK': 'Los Angeles Kings', 'SJS': 'San Jose Sharks',
    'CBJ': 'Columbus Blue Jackets', 'MIN': 'Minnesota Wild',
    'WPG': 'Winnipeg Jets', 'ARI': 'Arizona Coyotes',
    'VGK': 'Vegas Golden Knights'
}

# reverse of above
TEAM_LS = {
    'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI',
    'New York Rangers': 'NYR', 'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT', 'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF', 'Montréal Canadiens': 'MTL',
    'Ottawa Senators': 'OTT', 'Toronto Maple Leafs': 'TOR',
    'Carolina Hurricanes': 'CAR', 'Florida Panthers': 'FLA',
    'Tampa Bay Lightning': 'TBL', 'Washington Capitals': 'WSH',
    'Chicago Blackhawks': 'CHI', 'Detroit Red Wings': 'DET',
    'Nashville Predators': 'NSH', 'St. Louis Blues': 'STL',
    'Calgary Flames': 'CGY', 'Colorado Avalanche': 'COL',
    'Edmonton Oilers': 'EDM', 'Vancouver Canucks': 'VAN',
    'Anaheim Ducks': 'ANA', 'Dallas Stars': 'DAL',
    'Los Angeles Kings': 'LAK', 'San Jose Sharks': 'SJS',
    'Columbus Blue Jackets': 'CBJ', 'Minnesota Wild': 'MIN',
    'Winnipeg Jets': 'WPG', 'Arizona Coyotes': 'ARI',
    'Vegas Golden Knights': 'VGK'
}


DIVISION_TEAMS = {
    18: [1, 2, 3, 4, 5, 12, 15, 29],
    17: [6, 7, 8, 9, 10, 13, 14, 17],
    16: [16, 18, 19, 21, 25, 30, 52],
    15: [20, 22, 23, 24, 26, 28, 53, 54]
}

DIVISION_NAMES = {
    18: 'Metropolitan', 17: 'Atlantic', 16: 'Central', 15: 'Pacific'
}

CONFERENCE_TEAMS = {
    5: DIVISION_TEAMS[16] + DIVISION_TEAMS[15],
    6: DIVISION_TEAMS[18] + DIVISION_TEAMS[17]
}

CONFERENCE_NAMES = {
    5: 'Western', 6: 'Eastern'
}

HUMANIZE = {
    'games_played': ['Games Played', 'GP'],
    'wins': ['Wins', 'W'],
    'losses': ['Losses', 'L'],
    'ot_losses': ['OT Losses', 'OTL'],
    'ties': ['Ties', 'T'],
    'points': ['Points', 'P'],
    'pt_pct': ['Points Pct', 'P%'],
    'goals_for_pg': ['Goals For PG', 'GFPG'],
    'goals_ag_pg': ['Goals Against PG', 'GAPG'],
    'evgga_ratio': ['ES Goals Ratio', 'EVGR'],
    'pp_pct': ['Power Play Pct', 'PP%'],
    'pp_goals_for': ['Power Play Goals', 'PPGF'],
    'pp_opp': ['Power Play Opportunites', 'PP Opp'],
    'pk_pct': ['Penalty Kill Pct', 'PK%'],
    'pp_goals_ag': ['Power Play Goals Against', 'PPGA'],
    'shots_for_pg': ['Shots For PG', 'SFPG'],
    'shots_ag_pg': ['Shots Against PG', 'SAPG'],
    'win_score_first': ['Win Pct Score First', 'W% SF'],
    'win_opp_score_first': ['Win Pct Opp Score First', 'W% OSF'],
    'win_lead_first_per': ['Win Pct Lead First', 'W% LF'],
    'win_lead_second_per': ['Win Pct Leaf Second', 'W% LS'],
    'win_outshoot_opp': ['Win Pct Outshoot Opp', 'W% OS Opp'],
    'win_outshot_by_opp': ['Win Pct Outshot by Opp', 'W% Opp OS'],
    'faceoffs_taken': ['Faceoffs Taken', 'FO'],
    'faceoff_wins': ['Faceoffs Won', 'FOW'],
    'faceoff_losses': ['Faceoffs Lost', 'FOL'],
    'faceoff_pct': ['Faceoff Pct', 'FO%'],
    'save_pct': ['Save Pct', 'SV%'],
    'shooting_pct': ['Shooting Pct', 'S%'],
}
