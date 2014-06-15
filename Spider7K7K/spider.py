#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import aiohttp
import asyncio
from pyquery import PyQuery

BASE_URL = 'http://www.7k7k.com'

sem = asyncio.Semaphore(32)


@asyncio.coroutine
def get(url, *args, **kwargs):
    url = url.split('#')[0]
    with (yield from sem):
        response = yield from aiohttp.request('GET', url, *args, **kwargs)
    body = yield from response.read_and_close()
    body = body.decode('utf-8')
    print('GET', url)
    return body


def parser_index_dom(dom):
    data = []
    all_li = dom('div.box.waterfall.main-mod')('ul.ui-img-list>li')
    for li in all_li.items():
        for a in li('a').items():
            if a.has_class('li-top-a'):
                game_data = {
                    'name': a.text(),
                    'game_link': a.attr('href'),
                    'img': a('img').attr('src') or a('img').attr('lz_src'),
                }
                data.append(game_data)
    _uri = dom('a#waterfall_next.next-page-clickable').attr('href')
    next_url = None if _uri is None else '{}{}'.format(BASE_URL, _uri)
    return data, next_url


@asyncio.coroutine
def get_all_game(url, future):
    all_game = []
    while url:
        html = yield from get(url)
        dom = PyQuery(html)
        data, url = parser_index_dom(dom)
        all_game.extend(data)

    for g in all_game:
        g['game_link'] = '{}{}'.format(BASE_URL, g['game_link'])

    future.set_result(all_game)
    print('Get {} games'.format(len(all_game)))


def parser_game_dom(dom):
    pattern1 = re.compile('_gamepath')
    pattern2 = re.compile(r'\".+\"')

    for js in dom('head > script').items():
        js_text = js.text()
        for line in js_text.split('\n'):
            if pattern1.search(line):
                res = pattern2.findall(line)
                if res:
                    return res[0][1:-1]


@asyncio.coroutine
def correct_game_link(game_data):
    html1 = yield from get(game_data['game_link'])
    dom1 = PyQuery(html1)
    _uri = dom1('div.play-operate > a.ui-play-btn').attr('href')
    game_uri = '{}{}'.format(BASE_URL, _uri)

    html2 = yield from get(game_uri)
    dom2 = PyQuery(html2)
    real_url = parser_game_dom(dom2)
    game_data['game_link'] = real_url



if __name__ == '__main__':
    t = time.time()
    url = 'http://www.7k7k.com/tag/3271/'
    loop = asyncio.get_event_loop()

    # Get all games
    future = asyncio.Future()
    loop.run_until_complete(get_all_game(url, future))
    all_games = future.result()

    # Parser real game link
    tasks = [correct_game_link(g) for g in all_games]
    futures = asyncio.wait(tasks)
    loop.run_until_complete(futures)
    loop.close()

    # Write to json file
    with open('games.json', 'w') as fd:
        json.dump(all_games, fd, indent=4)
    print('Use {} sec'.format(int(time.time() - t)))
