import asyncio
import os
import sqlite3
import sys
from enum import Enum

import aiohttp

import puck.constants as const
import puck.database.db_constants as db_const
import puck.parser as parser
from puck.urls import Url
from puck.utils import async_request


def undefined_tables(db_conn):
    """Integrity check to see if this is first install or Data is Malformed"""
    result = db_conn.execute(db_const.GET_TABLES).fetchall()

    undefined = list(db_const.BASE_TABLES.keys())
    for row in result:
        # if the table is in base table remove it from the copy
        if row[0] in db_const.BASE_TABLES:
            undefined.remove(row[0])

    # return the list of tables not created
    return undefined


def create_base_tables(db_conn, to_create):
    """Base Table creation script."""

    for t in to_create:
        db_conn.execute(db_const.BASE_TABLES[t])

    db_conn.commit()


def create_base_triggers(db_conn):
    """Base Trigger creation script."""

    for t in db_const.BASE_TRIGGERS:
        try:
            db_conn.execute(t)
        # if the trigger exists ignore error
        except sqlite3.ProgammingError as err:
            print(f'Trigger already exists.')
            continue
    db_conn.commit()


async def populate_initial_tables(db_conn):
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
                    team_worker(team_id_q, session, db_conn, team_r_q)
                )
            )

        for i in range(3):
            tasks.append(
                asyncio.create_task(
                    roster_worker(team_r_q, session, db_conn, player_id_q)
                )
            )

        for i in range(3):
            tasks.append(
                asyncio.create_task(
                    player_worker(player_id_q, session, db_conn)
                )
            )

        # process team ids
        for _id in const.TEAM_ID.values():
            team_id_q.put_nowait(_id)
        # end of data indicators
        team_id_q.put_nowait(None)
        team_id_q.put_nowait(None)
        team_id_q.put_nowait(None)

        await asyncio.gather(*tasks, return_exceptions=False)


async def team_worker(queue, session, db_conn, result_queue):
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
        await parse_and_commit_team(team, db_conn, result_queue)
        # print(f'Finished Team: {waiting}')


async def roster_worker(queue, session, db_conn, result_queue):
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


async def player_worker(queue, session, db_conn):
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

        await parse_and_commit_player(player, db_conn)
        # print(f'Finished Player: {waiting}')


async def parse_and_commit_player(data, db_conn):
    parsed_data = parser.player_info_parser(data)

    try:
        insert_stmt(db_conn, 'player', parsed_data)
    except sqlite3.IntegrityError as ierr:
        # generally means this record already exists
        return
    except Exception as err:
        print(err)
        print(f'Data = {parsed_data}')


async def parse_team_roster(data, queue):
    for pers in data['roster']:
        await queue.put(pers['person']['id'])


async def parse_and_commit_team(data, db_conn, result_queue):
    parsed_data = parser.team_info_parser(data)

    insert_stmt(db_conn, 'team', parsed_data)

    # team.team_id is a FK for the players table therefore must be committed
    # prior to inserting players
    await result_queue.put(int(parsed_data['team_id']))


async def batch_update_db(_ids, db_conn, dispatcher):
    async with aiohttp.ClientSession() as session:
        workers = []
        for _id in _ids:
            workers.append(
                player_update_db(
                    db_conn, session, _id, dispatcher
                )
            )


async def player_update_db(db_conn, session, _id, dispatcher, params=None):
    """Async player update function.

    Args:
        db_conn (sqlite3.Connection): sqlite Connection
        session (aiohttp.ClientSession): aiohttp ClientSession
        _id (int): id can be game, player, team etc.
        dispatcher (Dispatch): Dispatch object holding all relevant details
        params (dict, optional): Url parameters. Defaults to None.
    """

    data = await async_request(
        dispatcher.url, session, {dispatcher.id_type: _id}, params
    )

    parsed_data = dispatcher.parser(data)

    update_stmt(
        db_conn, dispatcher.table, parsed_data, where=(dispatcher.id_type, _id)
    )


def select_stmt(db_conn, table, columns=None, joins=None, where=None, order_by=None) -> list:  # noqa
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
    base_str = "SELECT {} FROM {} "

    # holds the values for the query

    # if there are specific columns selected join them by ',' seperator
    if columns:
        # if using TableColumns Enum
        if isinstance(columns, db_const.TableColumns):
            columns = columns.value
        columns = ', '.join(columns)
    else:
        columns = '*'

    # format the base_str query string with columns and table
    base_str = base_str.format(columns, table)

    # TODO
    if joins:
        pass

    # where values are formatted here
    if where:
        base_str += "WHERE "
        stmts = []
        if isinstance(where, list):
            for w in where:
                # XXX: NO NEED TO PROTECT SQL INJECTION
                # for each where stmt format the column name and value
                stmts.append("{} = {}".format(w[0], w[1]))

            base_str += ', '.join(stmts)
        else:
            base_str += "{} = {}".format(where[0], where[1])

    if order_by:
        pass

    db_conn.row_factory = sqlite3.Row

    return db_conn.execute(base_str).fetchall()


def update_stmt(db_conn, table, params, where=None):
    """SQL Update statement creator and execution.

    Args:
        table (str): Name of the table to update
        params (dict): A dict containing column name + value to insert
        where (listof tuples, optional): A list of tuples containing where
                                        clauses. Defaults to None.
    """

    base_str = "UPDATE {} SET ".format(table)
    params = []
    stmt = []

    for key, val in params:
        stmt.append('{} = {}'.format(key, "?"))
        params.append(val)

    base_str += ", ".join(stmt)

    if where:
        base_str += " WHERE "
        stmt.clear()
        if isinstance(where, list):
            for w in where:
                stmt.append("{} = {}".format(w[0], "?"))
                params.append(w[1])
        else:
            stmt.append("{} = {}".format(where[0], "?"))
            params.append(where[1])

        base_str += ", ".join(stmt)

    db_conn.execute(base_str, tuple(params))
    db_conn.commit()


def insert_stmt(db_conn, table, params):
    """SQL Insert statement creator and execution.

    Args:
        db_conn (sqlite3.Connection): Connection object
        table (str): The table name
        params (tuple): Tuple of data to insert into the table
        columns (TableColumns or List, optional): List of column names,
                can use TableColumns Enum. Defaults to None.
    """
    base_str = "INSERT INTO {}({}) VALUES ({})"

    values = ", ".join("?" * len(params))

    data = []
    cols = []
    for key, val in params.items():
        cols.append(key)
        data.append(val)

    base_str = base_str.format(table, ', '.join(cols), values)

    db_conn.execute(base_str, tuple(data))
    db_conn.commit()


def connect_db() -> sqlite3.Connection:
    # this key always exist if we get this far
    db_path = os.environ['dbPath']

    # connect to the database
    db_conn = sqlite3.connect(database=db_path)

    # if the data is new setup the initial DB
    tables = undefined_tables(db_conn)

    if tables:
        print('Initializing base tables...')

        create_base_tables(db_conn, tables)
        create_base_triggers(db_conn)
        if 'team' in tables or 'player' in tables:
            asyncio.run(populate_initial_tables(db_conn))

    return db_conn
