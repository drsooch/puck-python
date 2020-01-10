import asyncio
import statistics
import sys

import aiohttp
import arrow

from puck.Games import BannerGame, FullGame, get_game_ids
from puck.urls import Url
from puck.utils import request


# ----------------- Simple Async -------------------------- #
async def get_data_f(url, _id, session):
    _url = url.value.format(_id)
    resp = await session.request(method='GET', url=_url)
    json = await resp.json()
    full = await init_full(_id, json)

    return full


async def main_f():
    gl = get_game_ids()

    async with aiohttp.ClientSession() as session:
        games = []
        for g in gl:
            games.append(get_data_f(Url.GAME, g, session))

        data = await asyncio.gather(*games)
    return data


async def get_data_b(url, _id, session):
    _url = url.value.format(_id)
    resp = await session.request(method='GET', url=_url)
    json = await resp.json()
    full = await init_banner(_id, json)

    return full


async def main_b():
    gl = get_game_ids()

    async with aiohttp.ClientSession() as session:
        games = []
        for g in gl:
            games.append(get_data_b(Url.GAME, g, session))

        data = await asyncio.gather(*games)
    return data

# ----------------- End Simple Async -------------------------- #

# ----------------- Async Class Init -------------------------- #


async def init_full(_id, game_info):
    return FullGame(_id, game_info)


async def init_banner(_id, game_info):
    return BannerGame(_id, game_info)

# ----------------- End Async Class Init -------------------------- #

# ----------------- Complex Async -------------------------- #


async def produce(qi, qr, session, n):
    while True:
        # print(f'worker: {n} getting...')
        _id = await qi.get()
        # print(f'worker: {n} requesting...')
        resp = await session.request(method='GET', url=Url.GAME.value.format(_id))
        # print(f'worker: {n} json...')
        json = await resp.json()

        await qr.put((_id, json))
        qi.task_done()


async def consume_f(q, games, n):
    while True:
        # print(f'consumer: {n} getting...')
        _id, json = await q.get()

        # print(f'consumer: {n} initializing...')
        game = await init_full(_id, json)
        games.append(game)
        q.task_done()


async def q_main_f():
    q_ids = asyncio.Queue()
    for game in get_game_ids():
        await q_ids.put(game)
    q_resp = asyncio.Queue()
    games = []
    async with aiohttp.ClientSession() as session:
        prods = [asyncio.create_task(
            produce(q_ids, q_resp, session, n)) for n in range(2)]
        cons = [asyncio.create_task(consume_f(q_resp, games, n))
                for n in range(5)]
        await q_ids.join()
        await q_resp.join()


async def consume_b(q, games, n):
    while True:
        # print(f'consumer: {n} getting...')
        _id, json = await q.get()

        # print(f'consumer: {n} initializing...')
        game = await init_banner(_id, json)
        games.append(game)
        q.task_done()


async def q_main_b():
    q_ids = asyncio.Queue()
    for game in get_game_ids():
        await q_ids.put(game)
    q_resp = asyncio.Queue()
    games = []
    async with aiohttp.ClientSession() as session:
        prods = [asyncio.create_task(
            produce(q_ids, q_resp, session, n)) for n in range(2)]
        cons = [asyncio.create_task(consume_b(q_resp, games, n))
                for n in range(5)]
        await q_ids.join()
        await q_resp.join()
# ----------------- End Complex Async -------------------------- #

# ----------------- Current Implementation -------------------------- #


def slow_f():
    gl = get_game_ids()
    games = []
    for g in gl:
        # print(f'{g} requesting... {arrow.now()}')
        resp = request(Url.GAME, {'game_id': g})
        # print(f'{g} initializing... {arrow.now()}')
        games.append(FullGame(g, resp))

    return games


def slow_b():
    gl = get_game_ids()
    games = []
    for g in gl:
        # print(f'{g} requesting... {arrow.now()}')
        resp = request(Url.GAME, {'game_id': g})
        # print(f'{g} initializing... {arrow.now()}')
        games.append(BannerGame(g, resp))

    return games


def calculate(data, name, f):
    mean = statistics.mean(data)
    median = statistics.median(data)
    stddev = statistics.pstdev(data)
    var = statistics.pvariance(data, mean)
    _min = min(data)
    _max = max(data)

    f.write(f'{name} Statistics: \n')
    f.write(f'Mean = {mean}\n')
    f.write(f'Median = {median}\n')
    f.write(f'Std Dev = {stddev}\n')
    f.write(f'Variance = {var}\n')
    f.write(f'Min = {_min}, Max = {_max}\n')
    f.write('\n')


if __name__ == "__main__":
    # curr_f = []
    # simp_f = []
    # comp_f = []
    # curr_b = []
    # simp_b = []
    # comp_b = []
    # begin = arrow.now()
    # for i in range(30):
    #     start = arrow.now()
    #     result = asyncio.run(main_f())
    #     simp_f.append((arrow.now() - start).total_seconds())
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Simple Async f', file=sys.stdout)

    #     start = arrow.now()
    #     result = asyncio.run(main_b())
    #     simp_b.append((arrow.now() - start).total_seconds())
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Simple Async b', file=sys.stdout)

    #     start = arrow.now()
    #     result = slow_f()
    #     curr_f.append((arrow.now() - start).total_seconds())
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Current f', file=sys.stdout)

    #     start = arrow.now()
    #     result = slow_b()
    #     curr_b.append((arrow.now() - start).total_seconds())
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Current b', file=sys.stdout)

    #     start = arrow.now()
    #     asyncio.run(q_main_f())
    #     comp_f.append(((arrow.now() - start).total_seconds()))
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Complex Async f', file=sys.stdout)

    #     start = arrow.now()
    #     asyncio.run(q_main_b())
    #     comp_b.append(((arrow.now() - start).total_seconds()))
    #     if i % 5:
    #         print('Total time: ' + str((arrow.now() - start).total_seconds()) +
    #               ' --> Complex Async b', file=sys.stdout)

    # with open('WifiInitSpeedTest02.txt', 'a') as f:
    #     calculate(curr_f, 'Current Full', f)
    #     calculate(curr_b, 'Current Banner', f)
    #     calculate(simp_f, 'Simple Async Full', f)
    #     calculate(simp_b, 'Simple Async Banner', f)
    #     calculate(comp_f, 'Complex Async Full', f)
    #     calculate(comp_b, 'Complex Async Banner', f)
    #     calculate(no_f, 'No Async Full', f)
    #     calculate(no_b, 'No Async Banner', f)
