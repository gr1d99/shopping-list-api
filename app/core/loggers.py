# -*- coding: utf-8 -*-

"""
Custom logger class to log errors and warnings of app during runtime.
"""

import os
import logging

from ..conf.settings import BASE_DIR

log_file = os.path.join(BASE_DIR, 'errors.log')


class AppLogger(object):
    """
    Logger class.
    """
    def __init__(self, name):
        """
        Initialize logger file handlers, formatters and streaming of logs.
        :param name: name of the context within which the log is executed.
        """

        self.logger = logging.Logger(name)
        self.logger.setLevel(logging.DEBUG)

        logger_handler = logging.FileHandler(log_file)
        logger_handler.setLevel(logging.DEBUG)

        logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(logger_formatter)

        logger_stream = logging.StreamHandler()
        logger_stream.setLevel(logging.DEBUG)

        self.logger.addHandler(logger_handler)
        self.logger.addHandler(logger_stream)
