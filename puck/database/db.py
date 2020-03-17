import asyncio
import os
import sys
from enum import Enum

import aiohttp
import psycopg2 as pg
import psycopg2.extras as pgext
import psycopg2.sql as pgsql

import puck.constants as const
import puck.database.db_constants as db_const
from puck.dispatcher import Dispatch
from puck.urls import Url
from puck.utils import ProgressBar, async_request


def undefined_tables(cursor):
    """Integrity check to see if this is first install or Data is Malformed"""
    cursor.execute(db_const.GET_TABLES)
    result = cursor.fetchall()

    undefined = list(db_const.BASE_TABLES.keys())
    for row in result:
        # if the table is in base table remove it from the copy
        if row[0] in db_const.BASE_TABLES:
            undefined.remove(row[0])

    # return the list of tables not created
    return undefined


def create_base_tables(cursor, to_create):
    """Base Table creation script."""

    for t in to_create:
        cursor.execute(db_const.BASE_TABLES[t])


def create_base_triggers(cursor):
    """Base Trigger creation script."""

    for t in db_const.BASE_TRIGGERS:
        cursor.execute(t)


async def populate_initial_tables(db_conn):
    """Async requests for Teams, Team rosters, and Players."""
    # NHL and AHL league ids/names
    for query in db_const.PRIMARY_DATA:
        db_conn.execute(query)

    num_workers = 5

    progress_bar = ProgressBar(end=1000)

    team_id_q = asyncio.Queue()
    team_r_q = asyncio.Queue()
    player_id_q = asyncio.Queue(30)

    tasks = []
    async with aiohttp.ClientSession() as session:
        # create workers
        for i in range(num_workers):
            tasks.append(
                asyncio.create_task(
                    generic_worker(
                        team_id_q, session, db_conn, team_r_q, progress_bar
                    )
                )
            )
            tasks.append(
                asyncio.create_task(
                    generic_worker(
                        player_id_q, session,
                        db_conn, pb=progress_bar
                    )
                )
            )
            tasks.append(
                asyncio.create_task(
                    generic_worker(
                        team_r_q, session, db_conn, player_id_q, progress_bar
                    )
                )
            )

        # process team ids
        for _id in const.TEAM_ID.values():
            team_id_q.put_nowait(Dispatch.team_info(_id))
            team_id_q.put_nowait(Dispatch.team_season(_id, 20172018))
            team_id_q.put_nowait(Dispatch.team_season(_id, 20182019))
            team_id_q.put_nowait(Dispatch.team_season(_id, 20192020))

        # end of data indicators
        for i in range(num_workers):
            team_id_q.put_nowait(Dispatch.empty('TEAM'))

        await asyncio.gather(*tasks, return_exceptions=False)

    progress_bar.completed()


async def generic_worker(queue, session, db_conn, result_queue=None, pb=None):
    """
    Generic Worker is a replacement of the old worker functions.
    It handles its queues and result_queues based on the dispatcher.

    All queues pass a Dispatch object with the required info.
    """
    while True:
        dispatcher = await queue.get()

        # handle end of data propogation
        if dispatcher.name in ['TEAM', 'ROSTER', 'PLAYER']:
            if result_queue is not None:
                if dispatcher.name == 'TEAM':
                    await result_queue.put(Dispatch.empty('ROSTER'))
                else:
                    await result_queue.put(Dispatch.empty('PLAYER'))
            break

        data = await async_request(
            dispatcher.url, session, {dispatcher.id_type: dispatcher.id},
            dispatcher.params
        )

        # Handle the dispatcher type based on name
        if dispatcher.name == 'team_season_stats':
            # dedicated function to handle complexity
            handle_team_season(db_conn, data, dispatcher)
            pb.increment(2)
        elif dispatcher.name == 'roster':
            parsed_data = dispatcher.parser(data)
            for person in parsed_data:
                await result_queue.put(
                    Dispatch.player_info(person)
                )
        elif dispatcher.name == 'team_info':
            parsed_data = dispatcher.parser(data)
            insert_stmt(db_conn, dispatcher.table, parsed_data)
            await result_queue.put(
                Dispatch.roster(parsed_data['team_id'])
            )
            pb.increment()
        elif dispatcher.name == 'player_info':
            parsed_data = dispatcher.parser(data)
            insert_stmt(db_conn, dispatcher.table, parsed_data)
            await handle_player_season(db_conn, dispatcher, parsed_data['position'], session)  # noqa
            pb.increment()


def handle_team_season(db_conn, data, dispatcher):
    """This is a complex case for populating initial tables."""
    # we need the season number nested in the dispatcher params
    season = dispatcher.params['season']
    # the parser will have the ids embedded
    parsed_data = dispatcher.parser(
        data, True, season
    )

    # pop that data out so we can insert into teams_season
    ts_data = parsed_data.pop('team_season')
    insert_stmt(db_conn, dispatcher.table, ts_data)

    # get the resultant unique_id for the second insert
    resp = select_stmt(
        db_conn, dispatcher.table, columns=['unique_id'],
        where=[(dispatcher.id_type, dispatcher.id), ('season', season)]
    )

    uid = resp[0]['unique_id']

    parsed_data['unique_id'] = uid

    # insert into team_season_stats
    insert_stmt(db_conn, 'team_season_stats', parsed_data)


async def handle_player_season(db_conn, dispatcher, pos, session):
    """Complex Handling of dealing with player stats"""

    # insert to the proper table
    if pos == 'G':
        new_disp = Dispatch.goalie_stats(dispatcher.id)
    else:
        new_disp = Dispatch.skater_stats(dispatcher.id)

    data = await async_request(
        new_disp.url, session, {new_disp.id_type: new_disp.id}
    )

    data = data['stats'][0]['splits']

    for year in range(len(data) - 1, -1, -1):
        if int(data[year]['season']) not in [20182019, 20192020]:
            break
        parsed_data = new_disp.parser(data[year])

        season_data = parsed_data.pop('season_data')
        season_data['player_id'] = dispatcher.id
        season = season_data['season']

        insert_stmt(db_conn, 'player_season', season_data)

        resp = select_stmt(
            db_conn, 'player_season', columns=['unique_id'],
            where=[
                (new_disp.id_type, new_disp.id), ('season', season),
                ('league_name', season_data['league_name']),
                ('team_name', season_data['team_name'])
            ]
        )

        uid = resp[0]['unique_id']
        parsed_data['unique_id'] = uid

        insert_stmt(db_conn, new_disp.table, parsed_data)


async def batch_update_db(_ids, db_conn, dispatcher):
    async with aiohttp.ClientSession() as session:
        workers = []
        for _id in _ids:
            workers.append(
                update_db(
                    db_conn, session, dispatcher(_id)
                )
            )

        await asyncio.gather(*workers)


async def update_db(db_conn, session, dispatcher, params=None):
    """Async update function.

    Args:
        db_conn (sqlite3.Connection): sqlite Connection
        session (aiohttp.ClientSession): aiohttp ClientSession
        dispatcher (Dispatch): Dispatch object holding all relevant details
        params (dict, optional): Url parameters. Defaults to None.
    """

    data = await async_request(
        dispatcher.url, session, {dispatcher.id_type: dispatcher.id}, params
    )
    parsed_data = dispatcher.parser(data)

    # check if record is in the table
    resp = select_stmt(
        db_conn, dispatcher.table, where=(dispatcher.id_type, dispatcher.id)
    )

    # if no record exists insert instead of update
    if not resp:
        insert_stmt(db_conn, dispatcher.table, parsed_data)
    else:
        update_stmt(
            db_conn, dispatcher.table, parsed_data,
            where=(dispatcher.id_type, dispatcher.id)
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
    base_str = pgsql.SQL("SELECT {} FROM {} {} ")
    table = pgsql.Identifier(table)
    values = []

    # holds the values for the query

    # if there are specific columns selected join them by ',' seperator
    if columns:
        # if using TableColumns Enum
        if isinstance(columns, db_const.TableColumns):
            columns = columns.value

        columns = pgsql.SQL(', ').join(map(pgsql.Identifier, columns))
    else:
        columns = pgsql.SQL('*')

    # TODO
    if joins:
        pass

    # where values are formatted here
    if where:
        where_clause = pgsql.SQL("WHERE {}")
        stmts = []
        if isinstance(where, list):
            for w in where:
                stmts.append(pgsql.SQL("{} = {}").format(
                    pgsql.Identifier(w[0]), pgsql.Placeholder()
                ))
                values.append(w[1])
            stmts = pgsql.SQL(", ").join(stmts)
        else:
            stmts = pgsql.SQL("{} = {}").format(
                pgsql.Identifier(where[0]), pgsql.Placeholder())
            values.append(where[1])

        where_clause = where_clause.format(stmts)
    else:
        where_clause = pgsql.SQL('')

    if order_by:
        pass

    base_str = base_str.format(columns, table, where_clause)

    # try:
    cursor = db_conn.cursor()
    cursor.execute(base_str, tuple(values))

    return cursor.fetchall()
    # except pg.Error as err:
    # print(base_str, values)
    # print(err)


def update_stmt(db_conn, table, params, where=None):
    """SQL Update statement creator and execution.

    Args:
        table (str): Name of the table to update
        params (dict): A dict containing column name + value to insert
        where (listof tuples, optional): A list of tuples containing where
                                        clauses. Defaults to None.
    """

    base_str = pgsql.SQL("UPDATE {} SET {} {}")
    data = []
    stmts = []

    table = pgsql.Identifier(table)

    for key, val in params.items():
        stmts.append(
            pgsql.SQL("{} = {}").format(
                pgsql.Identifier(key), pgsql.Placeholder()
            )
        )
        data.append(val)

    set_clause = pgsql.SQL(", ").join(stmts)

    if where:
        where_clause = pgsql.SQL("WHERE {}")
        stmts.clear()
        if isinstance(where, list):
            for w in where:
                stmts.append(
                    pgsql.SQL("{} = {}").format(
                        pgsql.Identifier(w[0]), pgsql.Placeholder()
                    )
                )
                data.append(w[1])
            stmts = pgsql.SQL(", ").join(stmts)
        else:
            stmts = pgsql.SQL("{} = {}").format(
                pgsql.Identifier(where[0]), pgsql.Placeholder()
            )
            data.append(where[1])

        where_clause = where_clause.format(stmts)
    else:
        where_clause = pgsql.SQL('')

    base_str = base_str.format(table, set_clause, where_clause)
    # try:
    cursor = db_conn.cursor()
    cursor.mogrify(base_str, tuple(data))
    cursor.execute(base_str, tuple(data))

    db_conn.commit()
    # except pg.Error as err:
    #     # from puck.debug import debug
    #     # debug('update_stmt.txt', base_str.as_string(cursor), str(data))
    #     print(base_str, data)
    #     print(err)


def insert_stmt(db_conn, table, params):
    """SQL Insert statement creator and execution.

    Args:
        db_conn (sqlite3.Connection): Connection object
        table (str): The table name
        params (tuple): Tuple of data to insert into the table
        columns (TableColumns or List, optional): List of column names,
                can use TableColumns Enum. Defaults to None.
    """
    base_str = pgsql.SQL("INSERT INTO {}({}) VALUES ({})")

    val_placeholder = pgsql.SQL(", ").join(pgsql.Placeholder() * len(params))

    data = []
    cols = []
    for key, val in params.items():
        cols.append(pgsql.Identifier(key))
        data.append(val)

    base_str = base_str.format(
        pgsql.Identifier(table), pgsql.SQL(", ").join(cols), val_placeholder
    )

# try:
    cursor = db_conn.cursor()
    cursor.execute(base_str, tuple(data))

    db_conn.commit()
# except pg.Error as err:
    # print(base_str, data)
    # print(err)


def get_ranked_stats(db_conn, table):
    return db_conn.execute(db_const.TEAM_RANKED_SELECT)


def connect_db() -> pg.extensions.connection:
    # these keys exist at this poioint
    db_name = os.environ['dbName']
    db_user = os.environ['dbUser']

    db_conn = pg.connect(
        database=db_name, user=db_user, cursor_factory=pgext.DictCursor
    )

    # use with so we close the cursor after scope is left
    cursor = db_conn.cursor()

    undef_tables = undefined_tables(cursor)

    if undef_tables:
        create_base_tables(cursor, undef_tables)
        create_base_triggers(cursor)
        db_conn.commit()

    cursor.close()

    return db_conn
