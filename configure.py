#coding=utf-8
import os
import json

class Config(object):
    config = None

    @classmethod
    def get_config(cls, name):
        if not cls.config:
            rel_path = '../config.json'
            cur_dir = os.path.split(os.path.realpath(__file__))[0]
            goal = os.path.join(cur_dir, rel_path)
            real_path = os.path.normpath(goal)
            
            with open(real_path) as f:
                data = json.load(f)
            cls.config = data['testing']

        return cls.config[name]
