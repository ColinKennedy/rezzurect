#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
from logging import handlers
import logging
import os


def attach_trace_level():
    trace_number = logging.DEBUG - 1
    logging.addLevelName(trace_number, 'TRACE')

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(trace_number):
            # Yes, logger takes its `*args` as `args`.
            self._log(trace_number, message, args, **kws)

    logger_class = logging.getLoggerClass()
    logger_class.trace = trace
    logging.TRACE = trace_number


def init():
    attach_trace_level()

    log_base_location = os.getenv('REZZURECT_LOG_PATH', '/tmp/.rezzurect')

    if not os.path.isdir(log_base_location):
        os.makedirs(log_base_location)

    logger = logging.getLogger('rezzurect')
    logger.setLevel(logging.TRACE)

    # Add the log message handler to the logger
    path = os.path.join(log_base_location, 'rezzurect.log')
    handler = handlers.RotatingFileHandler(path, maxBytes=50000000, backupCount=5)
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.TRACE)
    logger.addHandler(handler)
