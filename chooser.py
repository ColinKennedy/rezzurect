#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The module which is used to add and retrieve build & setting adapters.'''

# IMPORT STANDARD LIBRARIES
import platform
import os

# IMPORT LOCAL LIBRARIES
from .adapters.nuke import nuke_setting


_ADAPTERS = dict()


def get_build_adapter(
        package,
        version,
        system=platform.system(),
        architecture=platform.architecture(),
):
    '''Create an adapter for the given package configuration.

    This adapter is responsible for building the package.

    Args:
        package (str):
            The name of the Rez package to install.
        version (str):
            The specific install of `package`.
        system (str, optional):
            The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str, optional):
            The bits of the `system`. Example: "x86_64", "AMD64", etc.

    Raises:
        NotImplementedError:
            If no adapter could be found for the
            package/version/system/architecture.

    Returns:
        `BaseAdapter`: The found adapter.

    '''
    try:
        group = _ADAPTERS[package]
    except KeyError:
        raise NotImplementedError(
            'Package "{package}" is not supported. Options were, "{keys}"'.format(
                package=package, keys=list(_ADAPTERS)))

    try:
        adapter = group[system]
    except KeyError:
        raise NotImplementedError(
            'System "{system}" is not supported. Options were, "{keys}"'.format(
                system=system, keys=list(group)))

    return adapter(version, architecture)


# TODO : If aliases turn out to be useless on Windows then delete all
#        setting-adapter-related code since we won't need it anymore
#
def get_setting_adapter(package, version, alias=None):
    '''Create an adapter which can be used to add aliases to environment info.

    Args:
        package (str):
            The name of the package to get aliases of.
        version (str):
            The type of the `package` to get aliases of.
        alias (callable[str, str], optional):
            A handle to the aliases which is created when a package is installed.
            This handle is used to add aliases to the final package.

    Raises:
        NotImplementedError: If the given `package` has no adapter.

    Returns:
        `rezzurect.adapters.common.BaseAdapter`: The found adapter.

    '''
    adapters = {
        'nuke': nuke_setting.NukeAdapter,
    }

    try:
        adapter = adapters[package]
    except KeyError:
        raise NotImplementedError('Package "{package}" is not supported.'.format(package=package))

    return adapter(version, alias)


def add_common_commands(package, version, env, alias):
    '''Add aliases and environment variables for the given package.

    Args:
        package (str):
            The name of the package to get aliases of.
        version (str):
            The version provided by the package.
            It's up to the adapter to parse the version properly.
        env (`rez.utils.data_utils.AttrDictWrapper`):
            The Rez environment which represents `package`.
        alias (callable[str, str]):
            A handle to the aliases which is created when a package is installed.
            This handle is used to add aliases to the final package.

    '''
    adapter = get_setting_adapter(package, version, alias)
    adapter.execute()

    install_root = env.INSTALL_ROOT.get()

    if not os.path.isdir(install_root) or not os.listdir(install_root):
        package_adapter = get_build_adapter(package, version)

        for executable in package_adapter.get_preinstalled_executables():
            if os.path.isfile(executable):
                # Found a fallback system-wide install
                env.PATH.append(os.path.dirname(executable))
                break


def register_build_adapter(adapter, name, system):
    '''Add the given class for a platform.

    Args:
        adapter (`adapters.base_builder`):
            The adapter to add to our available build adapters.
        name (str):
            The name of the Rez package.
        system (str):
            The name of the OS which `adapter` represents.
            Example: "Darwin", "Linux", "Windows".

    '''
    _ADAPTERS.setdefault(name, dict())
    _ADAPTERS[name].setdefault(system, dict())

    _ADAPTERS[name][system] = adapter
