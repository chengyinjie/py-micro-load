#coding=utf-8
'''
场景控制
'''

from _global import *
from indicator import *
import result

import time
import traceback
from tornado import ioloop, gen
from tornado.queues import Queue
from threading import Thread

number = running = max_number = 0
jobs_todo = []
start_time = 0
timeout = 30
failed = 0      # 失败次数
last_response_time = 0  # 最后响应时间
qq = Queue()

settings = {
            'ramp up time': 0,      # 加载时间(ms)
            'launch time': 0,       # 启动间隔(ms)
            'batch launched': 1,    # 每批启动数量
            'run time': 0,          # 场景运行时间(s)
            'workers': 1,           # number of workers
            }

def add_users(users):
    global number
    for u in users:
        jobs_todo.append(u)
    number = len(users)

@gen.coroutine
def start():
    '''
    多用户场景
    '''
    if not jobs_todo:
        return
    
    global start_time, last_response_time
    last_response_time = start_time = time.time()

    monitor_thread = Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

    #n = len(jobs_todo)
    #rampup = settings['ramp up time']
    #if rampup:
    #    interval = rampup / 1000.0 / n

    start_workers(jobs_todo)
    yield qq.join()

    stat()

def start_workers(work):
    '''
    为每个worker划分工作并启动
    '''
    workers = settings['workers']
    total = len(work)
    part = int(round(total * 1.0 / workers))
    for i in range(0, total, part):
        job =  work[i: i+part]
        t = Thread(target=do_job, args=(job,))
        t.start()

@gen.coroutine
def do_job(jobs):
    for u in jobs:
        _start_user(u)

@gen.coroutine
def _start_user(user):
    '''
    开始一个独立用户
    如果设置了run time，可能需要运行多次
    '''
    i = 0
    _increase()
    while 1:
        t = time.time()
        try:
            yield user.work()

            elapsed_time = int((time.time() - t) * 1000)
            result.add(TOTAL_USER_TIME, elapsed_time)
            result.add(TOTAL_USERS, 1)
            result.add(TOTAL_REQUESTS, 1)
        except Exception, e:
            global failed
            failed += 1
            logger.error(hl(traceback.format_exc()))

        runtime = settings['run time']
        if not runtime:
            break

        elapsed_time = time.time() - start_time
        if elapsed_time >= runtime:
            break

        i += 1
        user.reset(i)
    _decrease()

@gen.coroutine
def _increase():
    logger.debug('increase user')
    yield qq.put(1)
    

@gen.coroutine
def _decrease():
    logger.debug('decrease number')
    yield qq.get()
    qq.task_done()

def stop():
    print('call stop')
    ioloop.IOLoop.instance().stop()
    stat()
    
def stat():
    # 用最后响应时间来做实际结束时间
    running_time = last_response_time - start_time
    running_time = settings['run time']
    workers = settings['workers']
    user_finished = result.get(TOTAL_USERS)
    reqs = result.get(TOTAL_REQUESTS)

    print
    print
    print('----------------------')
    print hl2('running time: %ds' % running_time)
    print hl2('number of workers: %d' % workers)
    print hl2('users per worker: %d' % (number/workers))
    print hl2('number of users: %d' % number)
    print hl2('max concurrency: %d' % max_number)
    print
    print hl2('total users: %d' % user_finished)
    print hl2('total requests: %d' % reqs)
    print
    print hl2('requests per sec: %.1f' % (reqs/running_time))
    print hl2('avg user time: %.f ms' % (0 if not user_finished else (result.get(TOTAL_USER_TIME) * 1.0 / user_finished)))
    print hl2('avg response time: %.f ms' % (0 if not reqs else (result.get(TOTAL_RESPONSE_TIME) * 1.0 / reqs)))

def monitor():
    '''
    守护线程
    监控场景运行状况
    '''
    runtime = settings['run time']
    while 1:
        logger.info('[monitor] qsize: %d' % qq.qsize())
        t = time.time()
        if t-start_time > runtime  and t-last_response_time > timeout:
            logger.warning('shutdown')
            logger.warning('%d coroutines still running' % running)
            stop()
        time.sleep(1)

def heartbeat():
    '''
    收到响应表示还在运行
    '''
    global last_response_time
    last_response_time = time.time()
