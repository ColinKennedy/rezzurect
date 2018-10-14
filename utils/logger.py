#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main logger environment for rezzurect.

`init` should be called once (and only once) to set up the parent logger which
all other loggers will inherit from.

'''

# IMPORT STANDARD LIBRARIES
from logging import handlers
import logging
import os


def attach_trace_level():
    '''Create a new log level called "TRACE" and make it some level below DEBUG.

    This level is meant for very spammy output which may be useful to see but
    don't make sense to put into DEBUG.

    '''
    trace_number = logging.DEBUG - 1
    logging.addLevelName(trace_number, 'TRACE')

    # TODO : If I can subclass `logging.Logger` and add trace as a proper
    #        method then do that. Otherwise, keep this hacky function
    #
    def trace(self, message, *args, **kws):
        '''Check if TRACE is enabled and, if so, log the given message.'''
        if self.isEnabledFor(trace_number):
            # Yes, logger takes its `*args` as `args`.
            self._log(trace_number, message, args, **kws)  # pylint: disable=protected-access

    logger_class = logging.getLoggerClass()
    logger_class.trace = trace
    logging.TRACE = trace_number


def init():
    '''Create a new log level called TRACE and create the parent rezzurect logger.'''
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
