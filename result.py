#coding=utf-8
'''
测试结果
'''

from threading import Lock
from indicator import *

_results = {
            TOTAL_USER_TIME: 0,
            TOTAL_USERS: 0,
            TOTAL_RESPONSE_TIME: 0,
            TOTAL_REQUESTS: 0,
            TOTAL_BYTES: 0,
            }

def append(k, v):
    if k not in _results:
        _results[k].append(v)

_add_lock = Lock()
def add(k, v=1):
    _add_lock.acquire()
    _results[k] = _results.get(k, 0) + v
    _add_lock.release()

def set(k, v):
    _results[k] = v

def get(k, default_value=None):
    return _results.get(k, default_value)
