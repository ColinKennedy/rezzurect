#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of commands which are used to help simplify Rez packages.'''

# IMPORT LOCAL LIBRARIES
from .setting_adapters import nuke_adapter


def get_setting_adapter(package, alias_manager=None):
    '''Create an adapter which can be used to add aliases to environment info.

    Args:
        package (str):
            The name of the package to get aliases of.
        alias_manager (`rez.rex.ActionManager.alias[str, str]`):
            A handle to the aliases which is created when a package is installed.
            This handle is used to add aliases to the final package.

    Raises:
        NotImplementedError: If the given `package` has no adapter.

    Returns:
        `rezzurect.adapters.common.BaseAdapter` or NoneType: The found class.

    '''
    adapters = {
        'nuke': nuke_adapter.NukeAdapter,
    }

    try:
        adapter = adapters[package]
    except KeyError:
        raise NotImplementedError('Package "{package}" is not supported.'.format(package=package))

    return adapter(alias_manager)


def add_common_commands(package, version, alias_manager):
    '''Add common aliases and environment variables for the given package.

    Args:
        package (str):
            The name of the package to get aliases of.
        version (str):
            The version provided by the package.
            It's up to the adapter to parse the version properly.
        alias_manager (`rez.rex.ActionManager.alias[str, str]`):
            A handle to the aliases which is created when a package is installed.
            This handle is used to add aliases to the final package.

    Returns:
        `rezzurect.adapters.common.BaseAdapter` or NoneType: The found class.

    '''
    adapter = get_setting_adapter(package, alias_manager)
    adapter.execute(version)
