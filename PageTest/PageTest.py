#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""页面链接可达性测试程序"""

import sys
if sys.version_info < (3, 5):
    print('Require the Python version >= 3.5')
    sys.exit(1)

try:
    import aiohttp
except ImportError:
    print('Require the `aiohttp` package')
    sys.exit(1)

import re
import time
import asyncio
import logging
import multiprocessing
from html.parser import HTMLParser

IDLE = 0
BUSY = 1


def get_logger(name, path, level=logging.INFO):
    '''获取 logger'''
    if name not in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatter = logging.Formatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            fmt='[%(asctime)s] %(message)s'
        )
        hdlr = logging.FileHandler(path)
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        return logger
    else:
        return logging.getLogger(name)

logger = get_logger("PageTestLog", 'page-test.log', logging.ERROR)


class Parser(HTMLParser):
    '''解析 html, 过滤出其中的链接'''
    def __init__(self, url, with_subdomain=False):
        HTMLParser.__init__(self)
        self.protocol, self.domain, self.path = self.parse_url(url)
        self.with_subdomain = with_subdomain
        self.links = set()

    def handle_starttag(self, tag, attrs):
        '''处理起始标签'''
        # 过滤 a 标签链接
        if tag == 'a':
            attrs = dict(attrs)
            url = attrs.get('href', '')
            self.handle_url(url)

    def parse_url(self, url):
        '''解析 url'''
        # 解析协议
        protocol_match = re.search(r'^.+(?=://)', url)
        protocol = protocol_match.group() if protocol_match else ''
        # 解析 domain
        domain_match = re.search(r'[\w-]+(\.[\w-]+)+(?=($|/))', url)
        domain = domain_match.group() if domain_match else ''
        # 解析 path
        path_match = re.search(r'(^|\b)/[^#]+', url)
        path = path_match.group() if path_match else ''
        return protocol, domain, path

    def handle_url(self, url):
        '''处理 url'''
        protocol, domain, path = self.parse_url(url)
        if path not in ['', '/']:
            # 对于只有 path 部分的链接, 将其设置为与当前页一致
            protocol = protocol or self.protocol
            domain = domain or self.domain
            if (self.with_subdomain and domain.endswith(self.domain)) \
                    or (not self.with_subdomain and domain == self.domain):
                # 重新组装 url, 补全了 protocol, domain, 去除了锚点
                url = '%s://%s%s' % (protocol, domain, path)
                self.links.add(url)

    def filter_urls(self, html):
        '''过滤 html 文本中的 url'''
        try:
            self.feed(html)
        except TypeError as e:
            if isinstance(html, bytes):
                return set()
            else:
                raise e
        return self.links


class Worker(multiprocessing.Process):
    '''工作进程'''
    def __init__(self, name, outbox, max_task):
        '''
        @name: 进程名, 为一个字符串格式的数字,
        @outbox: 用于回传解析到的 url 给主进程
        @max_task: 可开启的最大任务数 (即进程内并发执行的 coroutine 数量)
        '''
        multiprocessing.Process.__init__(self)
        self.name = name
        self.inbox = multiprocessing.Queue()  # 接收主进程分配的待处理 url
        self.outbox = outbox
        self.max_task = max_task

        self.doing = multiprocessing.Value('i', 0)
        self._doing = set()
        self.result = set()  # 暂存解析到的 url
        self.loop = None

    async def fetch(self, url, retry=3):
        '''请求 URL，并返回页面 HTML 文本'''
        try:
            start_time = self.loop.time()
            response = await aiohttp.request('GET', url)
            time_used = self.loop.time() - start_time
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            # 重试
            if retry > 0:
                retry -= 1
                await asyncio.sleep(1)
                return await self.fetch(url, retry)
            else:
                time_used = self.loop.time() - start_time
                logger.error('USE %6.3f s STAT: 500 URL: %s  (%s)'
                             % (time_used,  url, e))
                return ''
        except Exception as e:
            time_used = self.loop.time() - start_time
            logger.error('USE %6.3f s STAT: 500 URL: %s  (%s)'
                         % (time_used, url, e))
            return ''

        if not (200 <= response.status < 300):
            logger.error('USE %6.3f s STAT: %s URL: %s'
                         % (time_used, response.status, url))

        # 读取 html 文本，并返回
        body = await response.read()
        try:
            return body.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return body.decode('gbk')
            except UnicodeDecodeError:
                return body

    async def parse(self, url):
        '''解析 HTML 过滤其中的链接, 并将其存入 self.result'''
        html = await self.fetch(url)
        parser = Parser(url, with_subdomain=True)
        links = parser.filter_urls(html)
        self.result.update(links)
        logger.debug('Worker [%s] dug %s' % (self.name, len(links)))
        try:
            self._doing.remove(url)
            self.doing.value -= 1
        except KeyError:
            pass

    def reset_loop(self):
        '''重设 event loop'''
        asyncio.get_event_loop().close()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def handle_inbox(self):
        '''处理主进程分配的任务'''
        while True:
            try:
                if not self.inbox.empty() and self.doing.value < self.max_task:
                    # 取出待处理 url, 并生成 coroutine 处理
                    urls = self.inbox.get()
                    for url in urls:
                        self._doing.add(url)
                        self.doing.value += 1
                        asyncio.ensure_future(self.parse(url))
                if self.result:
                    # 保存结果到 self.outbox
                    done = []
                    for i in range(len(self.result)):
                        done.append(self.result.pop())
                    self.outbox.put(done)
                await asyncio.sleep(0.3)
            except KeyboardInterrupt:
                self.loop.stop()

    def run(self):
        logger.info('Worker [%s] start!' % self.name)
        # fork 之后创建新的 event_loop
        self.reset_loop()
        asyncio.async(self.handle_inbox())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()


def assignment_task(workers, todo, done):
    '''分配任务'''
    # 选出当前任务队列最少的进程
    worker = min(workers, key=lambda wk: wk.doing.value)

    # 删除已经处理过的 url
    urls = set(todo.get()) - done

    # 取出待处理的 url
    if urls:
        done.update(urls)
        worker.inbox.put(list(urls))


def any_working(workers):
    '''检查是否有非空闲进程'''
    return any(w.doing.value > 0 for w in workers)


def workers_exit(workers):
    '''退出工作进程'''
    for wk in workers:
        wk.terminate()
    logger.info('Main: Exit\n')


def main(url, worker_num=1, max_task=128):
    '''
    主函数

    @url: 入口 url
    @worker_num: 工作进程数量
    @max_task: 每个进程中最大任务数量
    '''
    todo = multiprocessing.Queue()  # 存放待处理 url
    done = set()  # 用于记录已完成或正在处理的 url，防止重复请求
    todo.put([url])

    # 初始化 workers
    assert worker_num > 0, '`worker_num` must greater than 0'
    workers = [Worker(str(i), todo, max_task) for i in range(worker_num)]
    for worker in workers:
        worker.start()

    while True:
        try:
            logger.info('Main: finished %s' % len(done))
            if not todo.empty():
                assignment_task(workers, todo, done)
                time.sleep(1)
            elif any_working(workers):
                time.sleep(1)
            else:
                # 当 todo 为空, 且 workers 全部为 IDLE 状态时, 程序结束
                workers_exit(workers)
                sys.exit(0)
        except KeyboardInterrupt:
            workers_exit(workers)
            sys.exit(0)


if __name__ == '__main__':
    worker_num = multiprocessing.cpu_count() or 1
    main('http://m.sohu.com/', worker_num, 2048)
