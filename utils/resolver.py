#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which is used to communicate with paths outside of Rezzurect.

Reference:
    https://github.com/ColinKennedy/tk-config-default2-respawn/wiki/Referring-To-Custom-Code

'''

# IMPORT STANDARD LIBRARIES
import logging
import copy

# IMPORT LOCAL LIBRARIES
from . import config


LOGGER = logging.getLogger('rezzurect.resolver')


def expand(text):
    '''Replace the given format text with an absolute path.

    Important:
        The keys which are used to expand `text` come from
        the user's environment settings. The only "reserved" key that the user
        may not modify is "respawn_root", which signifies the current path to
        the user's current Pipeline Configuration.

    Args:
        text (str): Some Python string to expand such as "{foo}/bar".

    Returns:
        str: The expanded text result.

    '''
    try:
        return text.format(**config.CUSTOM_KEYS)
    except KeyError:
        LOGGER.exception(
            'Text "%s" is missing one or more keys. Keys found, "%s".', text,
            config.CUSTOM_KEYS)
        raise


def expand_first(options, default=''):
    '''str: Try a number of different string options until one succeeds.'''
    for option in options:
        try:
            return expand(option)
        except KeyError:
            pass

    return default
