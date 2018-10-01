#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import platform
import os

# IMPORT LOCAL LIBRARIES
from .nuke import nuke_builder
from .nuke import nuke_setting


# TODO : Rename `get_adapter` to `get_package_adapter`
def get_adapter(
        package,
        version,
        system=platform.system(),
        architecture=platform.architecture(),
    ):
    '''Create an adapter for the given configuration.

    Args:
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

    Returns:
        `BaseAdapter`: The found adapter.

    '''
    options = {
        'nuke': {
            'Linux': nuke_builder.LinuxAdapter,
            'Windows': nuke_builder.WindowsAdapter,
        },
    }

    try:
        group = options[package]
    except KeyError:
        raise NotImplementedError(
            'Package "{package}" is not supported. Options were, "{keys}"'.format(
                package=package, keys=list(options)))

    try:
        adapter = group[system]
    except KeyError:
        raise NotImplementedError(
            'System "{system}" is not supported. Options were, "{keys}"'.format(
                system=system, keys=list(group)))

    return adapter(version, system, architecture)


def get_setting_adapter(package, version, alias=None):
    # '''Create an adapter which can be used to add aliases to environment info.

    # Args:
    #     package (str):
    #         The name of the package to get aliases of.
    #     alias (`rez.rex.ActionManager.alias[str, str]`):
    #         A handle to the aliases which is created when a package is installed.
    #         This handle is used to add aliases to the final package.

    # Raises:
    #     NotImplementedError: If the given `package` has no adapter.

    # Returns:
    #     `rezzurect.adapters.common.BaseAdapter` or NoneType: The found class.

    # '''
    adapters = {
        'nuke': nuke_setting.NukeAdapter,
    }

    try:
        adapter = adapters[package]
    except KeyError:
        raise NotImplementedError('Package "{package}" is not supported.'.format(package=package))

    return adapter(version, alias)


def add_common_commands(package, version, env, alias):
    # '''Add common aliases and environment variables for the given package.

    # Args:
    #     package (str):
    #         The name of the package to get aliases of.
    #     version (str):
    #         The version provided by the package.
    #         It's up to the adapter to parse the version properly.
    #     alias (`rez.rex.ActionManager.alias[str, str]`):
    #         A handle to the aliases which is created when a package is installed.
    #         This handle is used to add aliases to the final package.

    # Returns:
    #     `rezzurect.adapters.common.BaseAdapter` or NoneType: The found class.

    # '''
    adapter = get_setting_adapter(package, alias_manager)
    adapter.execute(version)
