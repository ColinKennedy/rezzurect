#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which adds build options for Rez packages.

Each build option is defined as a "strategy" which is basically just a name
and a callable function to run it.

See `register_strategy` for details on how to add build options to rezzurect.

'''

# IMPORT STANDARD LIBRARIES
import os

# IMPORT THIRD-PARTY LIBRARIES
from . import prepend_dict


STRATEGIES = prepend_dict.PrependOrderedDict()


def get_strategies(order=''):
    '''Find every build option in the order that the user requested.

    Args:
        order (`str`, optional):
            A comma-separated list of build option names to load.
            If nothing is given, the REZZURECT_STRATEGY_ORDER environment variable
            is sourced instead. If the environment variable is not defined
            then the order that build options were registered is used, instead.
            Default: "".

    Returns:
        list[tuple[str, callable]]: The found build option names and functions.

    '''
    if not order:
        order = []

        for item in os.getenv('REZZURECT_STRATEGY_ORDER', '').split(','):
            item.strip()

            if item:
                order.append(item)

    if not order:
        return list(STRATEGIES.items())

    strategies = []

    for item in order:
        try:
            strategies.append((item, STRATEGIES[item]))
        except KeyError:
            # TODO : Add logging message here
            pass

    return strategies


def register_strategy(name, function, priority=False):
    '''Add a build option to rezzurect with the given name.

    Args:
        name (str):
            The name which will be used to register the function.
        function (callable):
            A function that takes no args and will return nothing. If the build
            fails, this function will raise an exception
            (any type of exception is fine).
        priority (`bool`, optional):
            If True, add this build option to the front of the options.
            If False, add this build option to the end.
            Default is False.

    '''
    if priority:
        STRATEGIES.prepend(name, function)
    else:
        STRATEGIES[name] = function
