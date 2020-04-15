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

# KEY: [LONG_NAME, SHORT_NAME, PRECISION]
HUMANIZE = {
    # team stuff
    'games_played': ['Games Played', 'GP', None],
    'wins': ['Wins', 'W', None],
    'reg_ot_wins': ['ROW', 'ROW', None],
    'losses': ['Losses', 'L', None],
    'ot_losses': ['OT Losses', 'OTL', None],
    'streak': ['Streak', 'Streak', None],
    'last_ten': ['Last Ten', 'Last 10', None],
    'home_record': ['Home Record', 'Home', None],
    'away_record': ['Away Record', 'Away', None],
    'ties': ['Ties', 'T', None],
    'points': ['Points', 'P', None],
    'pt_pct': ['Points %', 'P%', 1],
    'goals_for_pg': ['Goals For PG', 'GFPG', 2],
    'goals_ag_pg': ['Goals Against PG', 'GAPG', 2],
    'evgga_ratio': ['ES Goals Ratio', 'EVGR', 3],
    'pp_pct': ['Power Play %', 'PP%', 1],
    'pp_goals_for': ['Power Play Goals', 'PPGF', None],
    'pp_opp': ['Power Play Opportunites', 'PP Opp', None],
    'pk_pct': ['Penalty Kill %', 'PK%', 1],
    'pp_goals_ag': ['Power Play Goals Against', 'PPGA', None],
    'shots_for_pg': ['Shots For PG', 'SFPG', 1],
    'shots_ag_pg': ['Shots Against PG', 'SAPG', 1],
    'win_score_first': ['Win % Score First', 'W% SF', 3],
    'win_opp_score_first': ['Win % Opp Score First', 'W% OSF', 3],
    'win_lead_first_per': ['Win % Lead First', 'W% LF', 3],
    'win_lead_second_per': ['Win % Leaf Second', 'W% LS', 3],
    'win_outshoot_opp': ['Win % Outshoot Opp', 'W% OS Opp', 3],
    'win_outshot_by_opp': ['Win % Outshot by Opp', 'W% Opp OS', 3],
    'faceoffs_taken': ['Faceoffs Taken', 'FO', None],
    'faceoff_wins': ['Faceoffs Won', 'FOW', None],
    'faceoff_losses': ['Faceoffs Lost', 'FOL', None],
    'faceoff_pct': ['Faceoff %', 'FO%', 1],
    'save_pct': ['Save %', 'SV%', 3],
    'shooting_pct': ['Shooting %', 'S%', 1],
    # player stuff
    'goals': ['Goals', 'G', None],
    'assists': ['Assists', 'A', None],
    'time_on_ice': ['Time On Ice', 'TOI', None],
    'pims': ['PIMS', 'PIMS', None],
    'hits': ['Hits', 'Hits', None],
    'pp_goals': ['Power Play Goals', 'PPG', None],
    'pp_assists': ['Power Play Assists', 'PPA', None],
    'pp_points': ['Power Play Points', 'PPP', None],
    'pp_toi': ['Power Play TOI', 'PP TOI', None],
    'sh_goals': ['Shorthanded Goals', 'SHG', None],
    'sh_assists': ['Shorthanded Assists', 'SHA', None],
    'sh_points': ['Shorthanded Points', 'SHP', None],
    'sh_toi': ['Shorthanded TOI', 'SH TOI', None],
    'ev_goals': ['Even Strength Goals', 'ESG', None],
    'ev_assists': ['Even Strength Assists', 'ESA', None],
    'ev_points': ['Even Strength Points', 'ESP', None],
    'ev_toi': ['Even Strength TOI', 'ES TOI', None],
    'faceoff_pct': ['Faceoff %', 'FO%', 1],
    'shooting_pct': ['Shooting %', 'SH%', 1],
    'gwg': ['Game Winning Goals', 'GWG', None],
    'ot_goals': ['OT Goals', 'OTG', None],
    'plus_minus': ['+/-', '+/-', None],
    'blocked': ['Blocked Shots', 'BS', None],
    'shifts': ['Shifts', 'Shifts', None]
}
