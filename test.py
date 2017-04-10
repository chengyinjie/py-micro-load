#coding=utf-8

import controller
from _global import *
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import gen
from tornado.ioloop import IOLoop

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

class U(object):
    def __init__(self):
        pass

    @gen.coroutine
    def work(self):
        url = 'http://help.baidu.com/question'
        req = HTTPRequest(url, method='GET')
        client = AsyncHTTPClient()
        response = yield client.fetch(req)
        raise gen.Return(response.body)

    def reset(self, *args):
        pass

if __name__ == '__main__':
    ctl = controller
    ctl.settings['run time'] = 10
    ctl.settings['connections'] = 20
    ctl.settings['workers'] = 2

    #JOBS_PER_WORK = 8
    #N = JOBS_PER_WORK * ctl.settings['workers']

    #users = [AuthUser(get_random_name()) for i in range(N)]
    #users = [TestUser(get_random_name()) for i in range(N)]
    #users = [AuthUser(get_random_name())]

    users = [U() for i in range(ctl.settings['connections'])]
    ctl.add_users(users)
    # ctl.start()
    IOLoop.current().run_sync(ctl.start)
