import asyncio
import os
import sqlite3
import sys

import aiohttp

from puck.urls import Url
from puck.utils import _TEAM_ID, async_request

PLAYERS_TABLE = """
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
    FOREIGN KEY("team_id") REFERENCES "team"("team_id"),
    PRIMARY KEY("player_id")
);"""

TEAMS_TABLE = """
CREATE TABLE "team" (
    "team_id"   INTEGER NOT NULL UNIQUE,
    "full_name" TEXT NOT NULL,
    "abbreviation"  TEXT NOT NULL CHECK(length("abbreviation") <= 3),
    "division"  INTEGER NOT NULL,
    "conference"    INTEGER NOT NULL,
    "active"    INTEGER CHECK("active" == 1 OR "active" == 0),
    "franchise_id" INTEGER NOT NULL,
    PRIMARY KEY("team_id")
);
    """

BASE_TABLES = {
    'player': PLAYERS_TABLE, 'team': TEAMS_TABLE
}


GET_TABLES = "SELECT tbl_name FROM sqlite_master WHERE type = 'table'"


def undefined_tables(conn):
    """Integrity check to see if this is first install or Data is Malformed"""
    result = conn.execute(GET_TABLES).fetchall()

    undefined = list(BASE_TABLES.keys())
    for row in result:
        # if the table is in base table remove it from the copy
        if row[0] in BASE_TABLES:
            undefined.remove(row[0])

    # return the list of tables not created
    return undefined


def create_base_tables(conn, to_create):
    """Base Table creation script."""

    for t in to_create:
        conn.execute(BASE_TABLES[t])

    conn.commit()


async def populate_initial_tables(conn):
    """Async requests for Teams, Team rosters, and Players."""

    team_id_q = asyncio.Queue()
    team_r_q = asyncio.Queue()
    player_id_q = asyncio.Queue(12)

    tasks = []
    async with aiohttp.ClientSession() as session:
        # create workers
        for i in range(3):
            tasks.append(
                asyncio.create_task(
                    team_worker(team_id_q, session, conn, team_r_q)
                )
            )

        for i in range(3):
            tasks.append(
                asyncio.create_task(
                    roster_worker(team_r_q, session, conn, player_id_q)
                )
            )

        for i in range(3):
            tasks.append(
                asyncio.create_task(
                    player_worker(player_id_q, session, conn)
                )
            )

        # process team ids
        for _id in _TEAM_ID.values():
            team_id_q.put_nowait(_id)
        # end of data indicators
        team_id_q.put_nowait(None)
        team_id_q.put_nowait(None)
        team_id_q.put_nowait(None)

        await asyncio.gather(*tasks, return_exceptions=False)


async def team_worker(queue, session, conn, result_queue):
    while True:
        waiting = await queue.get()
        # reached the end of the queue
        if waiting is None:
            # propogate the indicator
            await result_queue.put(None)
            if queue.empty():
                print('Team table finished.')
            break

        team = await async_request(
            Url.TEAMS, session,
            url_mods={'team_id': waiting}
        )
        await parse_and_commit_team(team, conn, result_queue)
        # print(f'Finished Team: {waiting}')


async def roster_worker(queue, session, conn, result_queue):
    while True:
        waiting = await queue.get()
        if waiting is None:
            # propogate indicator
            await result_queue.put(None)
            break

        roster = await async_request(
            Url.TEAM_ROSTER, session,
            url_mods={'team_id': waiting}
        )

        await parse_team_roster(roster, result_queue)
        # print(f'Finished Roster: {waiting}')
        # print(queue)


async def player_worker(queue, session, conn):
    while True:
        waiting = await queue.get()
        if waiting is None:
            if queue.empty():
                print('Player table finished.')
            break

        player = await async_request(
            Url.PLAYERS, session,
            url_mods={'player_id': waiting}
        )

        await parse_and_commit_player(player, conn)
        # print(f'Finished Player: {waiting}')


async def parse_and_commit_player(player, conn):
    player = player['people'][0]
    try:
        data = (
            player['id'], player['currentTeam']['id'], player['firstName'],
            player['lastName'], player.get('primaryNumber', ''),
            player['primaryPosition']['abbreviation'], player['shootsCatches'],
            player['rookie'], player['currentAge'], player['birthDate'],
            player['birthCity'], player.get('birthStateProvince', ''),
            player['birthCountry'], player['height'], player['weight']
        )
    except KeyError as e:
        # Some sort of failure with keys
        # keys that have propogated an error are used with get
        print(player)
        print(f'KeyError with: {e}. Player ID: {player["id"]}')
        conn.close()
        sys.exit(0)

    try:
        conn.execute(
            "INSERT INTO player VALUES \
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )
    except Exception as e:
        print(f'Data = {data}')

    conn.commit()


async def parse_team_roster(roster, queue):
    for pers in roster['roster']:
        await queue.put(pers['person']['id'])


async def parse_and_commit_team(team, conn, result_queue):
    team = team['teams'][0]
    data = (
        team['id'], team['name'], team['abbreviation'],
        team['division']['id'], team['conference']['id'],
        team['active'], team['franchiseId']
    )
    conn.execute("INSERT INTO team VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()

    # team.team_id is a FK for the players table therefore must be committed
    # prior to inserting players
    await result_queue.put(int(team['id']))


def select_stmt(table, columns=None, joins=None, where=None, order_by=None):  # noqa
    """SQL Select statement creator.
    Takes various options to build a valid SELECT statement.

    Args:
        table: (str) The table name

    Kwargs:
        columns (list of str, optional): A list of column names to return
        joins (list of str, optional): A list of joins
        where (list of tuple, optional): A list of where = val statements
                                        wrapped as a tuple
        order_by (list of str, optional): A list of order by column names

    Returns:
        str: A string containing the valid SQL SELECT statement.
    """
    base = "SELECT {} FROM {} "

    # if there are specific columns selected join them by ',' seperator
    if columns:
        columns = ','.join(columns)
    else:
        columns = '*'

    # format the base query string with columns and table
    base = base.format(columns, table)

    # TODO
    if joins:
        pass

    # any where values are formatted here
    if where:
        for w in where:
            base += "WHERE {} = {}".format(w[0], w[1])

    if order_by:
        pass

    print(base)

    return base


def connect_db():
    # this key always exist if we get this far
    db_path = os.environ['dbPath']

    # connect to the database
    conn = sqlite3.connect(database=db_path)

    # if the database is new setup the initial DB
    tables = undefined_tables(conn)

    if tables:
        print('Initializing base tables...')

        create_base_tables(conn, tables)
        asyncio.run(populate_initial_tables(conn))

    return conn
