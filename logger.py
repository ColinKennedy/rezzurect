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
            # Yes, logger takes its '*args' as 'args'.
            self._log(trace_number, message, args, **kws)

    logger_class = logging.getLoggerClass()
    logger_class.trace = trace
    logging.TRACE = trace_number


# TODO : Make this into a global logger
def get_logger(name):
    attach_trace_level()

    log_base_location = os.getenv('REZZURECT_LOG_PATH', '/tmp/.rezzurect')

    logger = logging.getLogger('rezzurect.{name}'.format(name=name))

    logger.setLevel(logging.TRACE)

    if not os.path.isdir(log_base_location):
        os.makedirs(log_base_location)

    path = os.path.join(log_base_location, 'rezzurect_{name}.log'.format(name=name))

    # Add the log message handler to the logger
    handler = handlers.RotatingFileHandler(path, maxBytes=50000000, backupCount=5)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
