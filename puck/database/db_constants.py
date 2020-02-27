"""
This file holds all Database constants i.e. Scripts, column names etc.

This file used to be part of the main db.py file but cluttered the file.
"""

from enum import Enum


class TableColumns(Enum):

    TEAM_TABLE_COLS = [
        "team_id", "full_name", "abbreviation",
        "division", "conference", "active",
        "franchise_id"
    ]

    BASE_GAME_COLS = [
        "team_id", "full_name", "abbreviation",
        "division", "conference", "franchise_id"
    ]

    PLAYER_TABLE_COLS = [
        "player_id", "team_id", "first_name",
        "last_name", "number", "position",
        "handedness", "rookie", "age",
        "birth_date", "birth_city", "birth_state",
        "birth_country", "height", "weight",
        "last_updated"
    ]

    PLAYER_INSERT_COLS = [
        "player_id", "team_id", "first_name",
        "last_name", "number", "position",
        "handedness", "rookie", "age",
        "birth_date", "birth_city", "birth_state",
        "birth_country", "height", "weight",
    ]


PLAYER_TABLE = """
CREATE TABLE "player" (
    "player_id"     INTEGER NOT NULL UNIQUE,
    "team_id"       INTEGER NOT NULL,
    "first_name"    TEXT NOT NULL,
    "last_name"     TEXT NOT NULL,
    "number"        TEXT,
    "position"      TEXT NOT NULL CHECK(
        "position" == "D" OR
        "position" == "G" OR
        "position" == "LW" OR
        "position" == "RW" OR
        "position" == "C"
        ),
    "handedness"    TEXT NOT NULL CHECK(
        "handedness" == "R" OR
        "handedness" == "L"
        ),
    "rookie"        INTEGER CHECK("rookie" == 0 OR "rookie" == 1),
    "age"           INTEGER,
    "birth_date"    TEXT,
    "birth_city"    TEXT,
    "birth_state"   TEXT,
    "birth_country" TEXT,
    "height"        TEXT,
    "weight"        INTEGER,
    "last_updated"  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY("team_id") REFERENCES "team"("team_id"),
    PRIMARY KEY("player_id")
);
"""


TEAM_TABLE = """
CREATE TABLE "team" (
    "team_id"       INTEGER NOT NULL UNIQUE,
    "full_name"     TEXT NOT NULL,
    "abbreviation"  TEXT NOT NULL CHECK(length("abbreviation") <= 3),
    "division"      INTEGER NOT NULL,
    "conference"    INTEGER NOT NULL,
    "active"        INTEGER CHECK("active" == 1 OR "active" == 0),
    "franchise_id"  INTEGER NOT NULL,
    PRIMARY KEY("team_id")
);
"""

PLAYER_SEASON_TABLE = """
CREATE TABLE "player_season" (
    "unique_id"     INTEGER UNIQUE,
    "player_id"     INTEGER NOT NULL,
    "season"        INTEGER NOT NULL,
    "league_id"     INTEGER,
    "league_name"   TEXT NOT NULL,
    "team_id"       INTEGER,
    "team_name"     TEXT NOT NULL,
    FOREIGN KEY("player_id") REFERENCES "player"("player_id"),
    PRIMARY KEY("unique_id" AUTOINCREMENT)
);
"""

SKATER_SEASON_STATS_TABLE = """
CREATE TABLE "skater_season_stats" (
    "unique_id"     INTEGER NOT NULL,
    "time_on_ice"   TEXT,
    "assists"       INTEGER,
    "goals"         INTEGER,
    "points"        INTEGER,
    "pims"          INTEGER,
    "shots"         INTEGER,
    "games"         INTEGER,
    "hits"          INTEGER,
    "pp_goals"      INTEGER,
    "pp_assists"    INTEGER,
    "pp_points"     INTEGER,
    "pp_toi"        TEXT,
    "sh_goals"      INTEGER,
    "sh_assists"    INTEGER,
    "sh_points"     INTEGER,
    "sh_toi"        TEXT,
    "ev_goals"      INTEGER,
    "ev_assists"    INTEGER,
    "ev_points"     INTEGER,
    "ev_toi"        TEXT,
    "faceoff_pct"   REAL,
    "shooting_pct"  REAL,
    "gwg"           INTEGER,
    "ot_goals"      INTEGER,
    "plus_minus"    INTEGER,
    "blocked"       INTEGER,
    "shifts"        INTEGER,
    PRIMARY KEY("unique_id"),
    FOREIGN KEY("unique_id") REFERENCES "player_season"("unique_id")
);
"""

GOALIE_SEASON_STATS_TABLE = """
CREATE TABLE "goalie_season_stats" (
    "unique_id"     INTEGER NOT NULL UNIQUE,
    "time_on_ice"   INTEGER,
    "shutouts"      INTEGER,
    "wins"          INTEGER,
    "losses"        INTEGER,
    "ot_losses"     INTEGER,
    "ties"          INTEGER,
    "saves"         INTEGER,
    "pp_saves"      INTEGER,
    "sh_saves"      INTEGER,
    "ev_saves"      INTEGER,
    "pp_shots"      INTEGER,
    "sh_shots"      INTEGER,
    "ev_shots"      INTEGER,
    "save_pct"      REAL,
    "gaa"           REAL,
    "games"         INTEGER,
    "games_started" INTEGER,
    "shots_against" INTEGER,
    "goals_against" INTEGER,
    "pp_save_pct"   REAL,
    "sh_save_pct"   REAL,
    "es_save_pct"   REAL,
    "last_updated"  TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("unique_id"),
    FOREIGN KEY("unique_id") REFERENCES "player_season"("unique_id")
);
"""

TEAM_SEASON_TABLE = """
CREATE TABLE "team_season" (
    "unique_id"     INTEGER NOT NULL UNIQUE,
    "team_id"       INTEGER NOT NULL,
    "season"        TEXT NOT NULL,
    "franchise_id"  INTEGER,
    "division_id"   INTEGER,
    "conference_id" INTEGER,
    PRIMARY KEY("unique_id" AUTOINCREMENT),
    FOREIGN KEY("team_id") REFERENCES "team"("team_id")
);
"""

TEAM_SEASON_STATS_TABLE = """
CREATE TABLE "team_season_stats" (
    "unique_id"             INTEGER NOT NULL UNIQUE,
    "games_played"          INTEGER,
    "wins"                  INTEGER,
    "losses"                INTEGER,
    "ot_losses"             INTEGER,
    "ties"                  INTEGER,
    "points"                INTEGER,
    "pt_pct"                REAL,
    "goals_for_pg"          REAL,
    "goals_ag_pg"           REAL,
    "evgga_ratio"           REAL,
    "pp_pct"                REAL,
    "pp_goals_for"          INTEGER,
    "pp_opp"                INTEGER,
    "pk_pct"                REAL,
    "pp_goals_ag"           INTEGER,
    "shots_for_pg"          REAL,
    "shots_ag_pg"           REAL,
    "win_score_first"       REAL,
    "win_opp_score_first"   REAL,
    "win_lead_first_per"    REAL,
    "win_lead_second_per"   REAL,
    "win_outshoot_opp"      REAL,
    "win_outshoot_by_opp"   REAL,
    "faceoffs_taken"        INTEGER,
    "faceoff_wins"          INTEGER,
    "faceoff_losses"        INTEGER,
    "faceoff_pct"           REAL,
    "save_pct"              REAL,
    "shooting_pct"          REAL,
    "last_updated"          TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY("unique_id") REFERENCES "team_season"("unique_id"),
    PRIMARY KEY("unique_id")
);
"""


UPDATE_TIME_P_TRIGGER = """
CREATE TRIGGER update_time_player AFTER UPDATE ON player
    BEGIN
        UPDATE player SET last_updated = CURRENT_TIMESTAMP
            WHERE player_id = NEW.player_id;
    END;
"""

UPDATE_TIME_TS_TRIGGER = """
CREATE TRIGGER update_time_team_stats AFTER UPDATE ON team_season_stats
    BEGIN
        UPDATE team_season_stats SET last_updated = CURRENT_TIMESTAMP
            WHERE player_id = NEW.player_id;
    END;
"""

UPDATE_TIME_GS_TRIGGER = """
CREATE TRIGGER update_time_goalie_stats AFTER UPDATE ON goalie_season_stats
    BEGIN
        UPDATE goalie_season_stats SET last_updated = CURRENT_TIMESTAMP
            WHERE unique_id = NEW.unique_id;
    END;
"""

UPDATE_TIME_SS_TRIGGER = """
CREATE TRIGGER update_time_skater_stats AFTER UPDATE ON skater_season_stats
    BEGIN
        UPDATE skater_season_stats SET last_updated = CURRENT_TIMESTAMP
            WHERE unique_id = NEW.unique_id;
    END;
"""

COMPUTE_ASSISTS_INS_TRIGGER = """
CREATE TRIGGER compute_assists_ins AFTER INSERT ON skater_season_stats
BEGIN
    UPDATE skater_season_stats
        SET pp_assists = (new.pp_points - new.pp_goals),
            ev_assists = (new.ev_points - new.ev_goals),
            sh_assists = (new.sh_points - new.sh_goals)
        WHERE
            unique_id = new.unique_id;
END;
"""

COMPUTE_ASSISTS_UPD_TRIGGER = """
CREATE TRIGGER compute_assists_upd AFTER INSERT
ON skater_season_stats
BEGIN
    UPDATE skater_season_stats
        SET pp_assists = (new.pp_points - new.pp_goals),
            ev_assists = (new.ev_points - new.ev_goals),
            sh_assists = (new.sh_points - new.sh_goals)
        WHERE
            unique_id = new.unique_id;
END;
"""

BASE_TABLES = {
    'player': PLAYER_TABLE, 'team': TEAM_TABLE,
    'player_season': PLAYER_SEASON_TABLE,
    'skater_season_stats': SKATER_SEASON_STATS_TABLE,
    'goalie_season_stats': GOALIE_SEASON_STATS_TABLE,
    'team_season': TEAM_SEASON_TABLE,
    'team_season_stats': TEAM_SEASON_STATS_TABLE
}

BASE_TRIGGERS = [
    UPDATE_TIME_P_TRIGGER, UPDATE_TIME_TS_TRIGGER, UPDATE_TIME_SS_TRIGGER,
    UPDATE_TIME_GS_TRIGGER, COMPUTE_ASSISTS_INS_TRIGGER,
    COMPUTE_ASSISTS_UPD_TRIGGER
]


GET_TABLES = """SELECT tbl_name FROM sqlite_master WHERE type = 'table'"""
