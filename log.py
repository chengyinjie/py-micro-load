#coding=utf-8

import os
import json
import logging
import logging.config

class Log(object):
    _logger = None

    @classmethod
    def setup_logging(cls):
        rel_path = '../config.json'
        cur_dir = os.path.split(os.path.realpath(__file__))[0]
        goal = os.path.join(cur_dir, rel_path)
        real_path = os.path.normpath(goal)
        
        try:
            with open(real_path) as f:
                data = json.load(f)
            log_config = data['log']
            logging.config.dictConfig(log_config)
        except Exception, e:
            logging.basicConfig(level=logging.INFO)
            logging.warning('log setup failed', exc_info=True)

    @classmethod
    def get_logger(cls):
        if not cls._logger:
            cls.setup_logging()
            logger = logging.getLogger(__name__)
            cls._logger = logger
            logger.debug('logger init')
        return cls._logger
