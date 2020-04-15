"""
This file holds all Database constants i.e. Scripts, column names etc.

This file used to be part of the main db.py file but cluttered the file.
"""

from enum import Enum


class TableColumns(Enum):
    BASE_TEAM_CLASS = [
        "team_id", "full_name", "abbreviation",
        "division", "conference", "franchise_id"
    ]

    BASE_PLAYER_CLASS = [
        "team_id", "first_name",
        "last_name", "number", "position",
        "handedness", "rookie", "age",
    ]

    TEAM_SEASON_CLASS = [
        "games_played", "wins", "losses", "ot_losses", "points", "pt_pct",
        "goals_for_pg", "goals_ag_pg", "evgga_ratio", "pp_pct", "pp_goals_for",
        "pp_opp", "pk_pct", "pp_goals_ag", "shots_for_pg", "shots_ag_pg",
        "win_score_first", "win_opp_score_first", "win_lead_first_per",
        "win_lead_second_per", "win_outshoot_opp", "win_outshot_by_opp",
        "faceoffs_taken", "faceoff_wins", "faceoff_pct", "save_pct",
        "shooting_pct"
    ]


LEAGUE_TABLE = """
CREATE TABLE IF NOT EXISTS league (
    league_id     INTEGER NOT NULL PRIMARY KEY,
    league_name   VARCHAR(40) NOT NULL
);
"""

TEAM_TABLE = """
CREATE TABLE IF NOT EXISTS team (
    team_id       INTEGER NOT NULL PRIMARY KEY,
    full_name     VARCHAR(50) NOT NULL,
    abbreviation  VARCHAR(3),
    division      SMALLINT,
    conference    SMALLINT,
    active        BOOLEAN,
    franchise_id  SMALLINT,
    league_id     INTEGER NOT NULL REFERENCES league
);
"""

PLAYER_TABLE = """
CREATE TABLE IF NOT EXISTS player (
    player_id     INTEGER NOT NULL PRIMARY KEY,
    team_id       INTEGER NOT NULL REFERENCES team,
    first_name    VARCHAR(30) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    number        VARCHAR(2),
    position      VARCHAR(2) NOT NULL CHECK (
        position IN ('G', 'LW', 'RW', 'D', 'C')
        ),
    handedness    VARCHAR(1) NOT NULL CHECK(
        handedness IN ('L', 'R')
        ),
    rookie        BOOLEAN,
    age           SMALLINT,
    birth_date    VARCHAR(50),
    birth_city    VARCHAR(50),
    birth_state   VARCHAR(50),
    birth_country VARCHAR(50),
    height        VARCHAR(7),
    weight        SMALLINT,
    last_updated  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


PLAYER_SEASON_TABLE = """
CREATE TABLE IF NOT EXISTS player_season (
    unique_id     SERIAL NOT NULL PRIMARY KEY,
    player_id     INTEGER NOT NULL REFERENCES player,
    season        INTEGER NOT NULL,
    league_id     INTEGER NOT NULL REFERENCES league,
    league_name   VARCHAR(50) NOT NULL,
    team_id       INTEGER,
    team_name     VARCHAR(50) NOT NULL
);
"""

SKATER_SEASON_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS skater_season_stats (
    unique_id     INTEGER NOT NULL PRIMARY KEY REFERENCES player_season,
    time_on_ice   VARCHAR(15),
    assists       SMALLINT,
    goals         SMALLINT,
    points        SMALLINT,
    pims          SMALLINT,
    shots         SMALLINT,
    games         SMALLINT,
    hits          SMALLINT,
    pp_goals      SMALLINT,
    pp_assists    SMALLINT,
    pp_points     SMALLINT,
    pp_toi        VARCHAR(15),
    sh_goals      SMALLINT,
    sh_assists    SMALLINT,
    sh_points     SMALLINT,
    sh_toi        VARCHAR(15),
    ev_goals      SMALLINT,
    ev_assists    SMALLINT,
    ev_points     SMALLINT,
    ev_toi        VARCHAR(15),
    faceoff_pct   REAL,
    shooting_pct  REAL,
    gwg           SMALLINT,
    ot_goals      SMALLINT,
    plus_minus    SMALLINT,
    blocked       SMALLINT,
    shifts        SMALLINT,
    last_updated  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

GOALIE_SEASON_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS goalie_season_stats (
    unique_id     INTEGER NOT NULL PRIMARY KEY REFERENCES player_season,
    time_on_ice   INTEGER,
    shutouts      SMALLINT,
    wins          SMALLINT,
    losses        SMALLINT,
    ot_losses     SMALLINT,
    ties          SMALLINT,
    saves         SMALLINT,
    pp_saves      SMALLINT,
    sh_saves      SMALLINT,
    ev_saves      SMALLINT,
    pp_shots      SMALLINT,
    sh_shots      SMALLINT,
    ev_shots      SMALLINT,
    save_pct      REAL,
    gaa           REAL,
    games         SMALLINT,
    games_started SMALLINT,
    shots_against SMALLINT,
    goals_against SMALLINT,
    pp_save_pct   REAL,
    sh_save_pct   REAL,
    ev_save_pct   REAL,
    last_updated  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TEAM_SEASON_TABLE = """
CREATE TABLE IF NOT EXISTS team_season (
    unique_id     SERIAL NOT NULL PRIMARY KEY,
    team_id       INTEGER NOT NULL REFERENCES team,
    season        INTEGER NOT NULL,
    franchise_id  SMALLINT,
    division_id   SMALLINT,
    conference_id SMALLINT
);
"""

TEAM_SEASON_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS team_season_stats (
    unique_id             INTEGER NOT NULL PRIMARY KEY REFERENCES team_season,
    games_played          SMALLINT,
    wins                  SMALLINT,
    losses                SMALLINT,
    ot_losses             SMALLINT,
<<<<<<< HEAD
    reg_ot_wins           SMALLINT,
    streak                VARCHAR(7),
    last_ten              VARCHAR(7),
    home_record           VARCHAR(9),
    away_record           VARCHAR(9),
=======
    reg_wins              SMALLINT,
>>>>>>> 6ef19c728f435d8fe1965f3d9891b980e7d00a63
    ties                  SMALLINT,
    points                SMALLINT,
    pt_pct                REAL,
    goals_for_pg          REAL,
    goals_ag_pg           REAL,
    evgga_ratio           REAL,
    pp_pct                REAL,
    pp_goals_for          SMALLINT,
    pp_opp                SMALLINT,
    pk_pct                REAL,
    pp_goals_ag           SMALLINT,
    shots_for_pg          REAL,
    shots_ag_pg           REAL,
    win_score_first       REAL,
    win_opp_score_first   REAL,
    win_lead_first_per    REAL,
    win_lead_second_per   REAL,
    win_outshoot_opp      REAL,
    win_outshot_by_opp    REAL,
    faceoffs_taken        SMALLINT,
    faceoff_wins          SMALLINT,
    faceoff_losses        SMALLINT,
    faceoff_pct           REAL,
    save_pct              REAL,
    shooting_pct          REAL,
    last_updated          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TEAM_RANKED_SELECT = """SELECT
    games_played,
    streak,
    last_ten,
    home_record,
    away_record,
    wins,
    RANK() OVER (ORDER BY wins DESC) AS wins_rank,
    losses,
    RANK() OVER (ORDER BY losses ASC) AS losses_rank,
    ot_losses,
    RANK() OVER (ORDER BY ot_losses ASC) AS ot_losses_rank,
<<<<<<< HEAD
    reg_ot_wins,
    RANK() OVER (ORDER BY reg_ot_wins DESC) AS reg_ot_wins_rank,
=======
    reg_wins,
    RANK() OVER (ORDER BY reg_wins DESC) AS reg_wins_rank,
>>>>>>> 6ef19c728f435d8fe1965f3d9891b980e7d00a63
    points,
    RANK() OVER (ORDER BY points DESC) AS points_rank,
    pt_pct,
    RANK() OVER (ORDER BY pt_pct DESC) AS pt_pct_rank,
    goals_for_pg,
    RANK() OVER (ORDER BY goals_for_pg DESC) AS goals_for_pg_rank,
    goals_ag_pg,
    RANK() OVER (ORDER BY goals_ag_pg ASC) AS goals_ag_pg_rank,
    evgga_ratio,
    RANK() OVER (ORDER BY evgga_ratio DESC) AS evgga_ratio_rank,
    pp_pct,
    RANK() OVER (ORDER BY pp_pct DESC) AS pp_pct_rank,
    pp_goals_for,
    RANK() OVER (ORDER BY pp_goals_for DESC) AS pp_goals_for_rank,
    pp_opp,
    RANK() OVER (ORDER BY pp_opp DESC) AS pp_opp_rank,
    pk_pct,
    RANK() OVER (ORDER BY pk_pct DESC) AS pk_pct_rank,
    pp_goals_ag,
    RANK() OVER (ORDER BY pp_goals_ag ASC) AS pp_goals_ag_rank,
    shots_for_pg,
    RANK() OVER (ORDER BY shots_for_pg DESC) AS shots_for_pg_rank,
    shots_ag_pg,
    RANK() OVER (ORDER BY shots_ag_pg ASC) AS shots_ag_pg_rank,
    faceoffs_taken,
    RANK() OVER (ORDER BY faceoffs_taken DESC) AS faceoffs_taken_rank,
    faceoff_wins,
    RANK() OVER (ORDER BY faceoff_wins DESC) AS faceoff_wins_rank,
    faceoff_losses,
    RANK() OVER (ORDER BY faceoff_losses ASC) AS faceoff_losses_rank,
    faceoff_pct,
    RANK() OVER (ORDER BY faceoff_pct DESC) AS faceoff_pct_rank,
    save_pct,
    RANK() OVER (ORDER BY save_pct DESC) AS save_pct_rank,
    shooting_pct,
    RANK() OVER (ORDER BY shooting_pct DESC) AS shooting_pct_rank
    FROM team_season_stats
        INNER JOIN team_season ON
        team_season.unique_id = team_season_stats.unique_id
        AND team_season.season = {}
        ORDER BY team_season.team_id;"""

TOP_SCORER_TEAM = """
SELECT
player_id,
goals,
RANK() OVER (ORDER BY goals DESC) as goals_rank,
assists,
RANK() OVER (ORDER BY assists DESC) as assists_rank,
points,
RANK() OVER (ORDER BY points DESC) as points_rank
FROM skater_season_stats
INNER JOIN player_season
    ON player_season.unique_id = skater_season_stats.unique_id
    AND player_season.team_id = {}
    AND player_season.season = {}
ORDER BY player_id ASC;
"""

UT_PLAYER_FUNC_TRIG = """
CREATE OR REPLACE FUNCTION update_time_player() RETURNS trigger AS
    $$
    BEGIN
        NEW.last_updated = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;

CREATE TRIGGER player_last_update
AFTER UPDATE ON player
EXECUTE PROCEDURE update_time_player();
"""

UT_TS_FUNC_TRIG = """
CREATE FUNCTION update_time_team_stats() RETURNS trigger AS
    $$
    BEGIN
        NEW.last_updated = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;

CREATE TRIGGER ts_stat_last_update
AFTER UPDATE ON team_season_stats
EXECUTE PROCEDURE update_time_team_stats();
"""

UT_GS_FUNC_TRIG = """
CREATE FUNCTION update_time_goalie_stats() RETURNS trigger AS
    $$
    BEGIN
        NEW.last_updated = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;

CREATE TRIGGER g_stat_last_update
AFTER UPDATE ON goalie_season_stats
EXECUTE PROCEDURE update_time_goalie_stats();
"""

UT_SS_FUNC_TRIG = """
CREATE FUNCTION update_time_skater_stats() RETURNS trigger AS
    $$
    BEGIN
        NEW.last_updated = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;

CREATE TRIGGER s_stats_last_update
AFTER UPDATE ON skater_season_stats
EXECUTE PROCEDURE update_time_skater_stats();
"""


CP_PTS_FUNC_TRIG = """
CREATE FUNCTION compute_points() RETURNS trigger AS
    $$
    BEGIN
        NEW.ev_points  = (NEW.points - NEW.pp_points - NEW.sh_points);
        NEW.ev_goals   = (NEW.goals - NEW.pp_goals - NEW.sh_goals);
        NEW.pp_assists = (NEW.pp_points - NEW.pp_goals);
        NEW.ev_assists = (NEW.ev_points - NEW.ev_goals);
        NEW.sh_assists = (NEW.sh_points - NEW.sh_goals);
        RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;

CREATE TRIGGER comp_points_ins
AFTER INSERT ON skater_season_stats
EXECUTE PROCEDURE compute_points();

CREATE TRIGGER comp_points_upd
AFTER UPDATE ON skater_season_stats
EXECUTE PROCEDURE compute_points();
"""

BASE_TABLES = {
    'league': LEAGUE_TABLE, 'team': TEAM_TABLE, 'player': PLAYER_TABLE,
    'player_season': PLAYER_SEASON_TABLE,
    'skater_season_stats': SKATER_SEASON_STATS_TABLE,
    'goalie_season_stats': GOALIE_SEASON_STATS_TABLE,
    'team_season': TEAM_SEASON_TABLE,
    'team_season_stats': TEAM_SEASON_STATS_TABLE,
}

BASE_TRIGGERS = [
    UT_GS_FUNC_TRIG, UT_PLAYER_FUNC_TRIG, UT_SS_FUNC_TRIG,
    UT_TS_FUNC_TRIG, CP_PTS_FUNC_TRIG
]


GET_TABLES = """
SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public';
"""
PRIMARY_DATA = [
    """INSERT INTO league(league_id, league_name) VALUES (133, 'National Hockey League');""",
    """INSERT INTO league(league_id, league_name) VALUES (153, 'American Hockey League');"""
]

RESET_DATABASE = """
DROP TABLE team_season_stats;
DROP TABLE team_season;
DROP TABLE skater_season_stats;
DROP TABLE goalie_season_stats;
DROP TABLE player_season;
DROP TABLE player;
DROP TABLE team;
DROP TABLE league;

DROP FUNCTION public.compute_points();
DROP FUNCTION public.update_time_goalie_stats();
DROP FUNCTION public.update_time_player();
DROP FUNCTION public.update_time_skater_stats();
DROP FUNCTION public.update_time_team_stats();
"""
