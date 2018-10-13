#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module which is used to initialize Rez-build options.'''

# IMPORT STANDARD LIBRARIES
import functools
import platform
import imp
import os
import re

# IMPORT LOCAL LIBRARIES
from .strategies import strategy
from .utils import common
from . import chooser


def _get_rez_environment_details():
    # TODO : There has to be a better way to query this info. Find out, later
    request = re.compile(r'~(\w+)==(\w+)')

    output = {key: value for key, value in request.findall(os.environ.get('REZ_REQUEST', ''))}
    platform_ = output['platform'].capitalize()
    return (platform_, output['os'], output['arch'])


def _resolve_object(path):
    '''Convert a path to a Python module into a Python module.

    Args:
        path (str):
            A path that is one of two syntaxes. /absolute/path/to/module.py or
            to.module (assuming that this module is importable in the user's PYTHONPATH).

    Returns:
        `module` or NoneType: The found module, if any.

    '''
    if os.path.isabs(path):
        try:
            return imp.load_source('', path)
        except ImportError:
            return

    try:
        module = __import__(path)
    except ImportError:
        return

    modules = path.split('.')
    item = module

    for index in range(1, len(modules)):
        item = getattr(item, modules[index])

    return item


def _get_handlers(objects=None):
    r'''Create the functions that will be used to add user "build" adapters.

    By default, if no objects are given, rezzurect will provide its own to use.
    It's highly encouraged to provide your own modules and classes though because
    every pipeline is different and you should customize packages for your needs.

    To provide own modules/classes, add paths to Python files or Python packages
    into the REZZURECT_ENVIRONMENT_MODULES environment variable.

    Args:
        objects (str):
            A path-separated list of paths or Python modules. Example:

            C:\Users\foo\bar.py;some.importable.path;os.path
            /usr/foo/bar.py:some.importable.path:os.path

            A path that is one of two syntaxes. /absolute/path/to/module.py or
            to.module (assuming that this module is importable in the user's PYTHONPATH).

    Returns:
        list[callable]: The found functions.

    '''
    if not objects:
        objects = []

        for obj in os.getenv('REZZURECT_ENVIRONMENT_MODULES', '').split(os.pathsep):
            obj = obj.strip()

            if obj:
                objects.append(obj)

    paths = ['rezzurect._environment']  # This is a fallback path for "default" handlers

    if objects:
        paths = []

        for module in objects:
            module = module.strip()

            if module:
                paths.append(module)

    handlers = []

    for path in paths:
        module = _resolve_object(path)

        if not module:
            # TODO : Add a logging statement here
            continue

        handlers.append(module.main)

    return handlers


def _make_install_and_install_with_local(adapter, source_path, install_path):
    if not os.path.isdir(install_path):
        os.makedirs(install_path)

    adapter.install_from_local(source_path, install_path)


def _init(
        package,
        version,
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    '''Load all of the user's defined build methods.

    If no build methods were specified, a set of default build methods are
    sourced by rezzurect, automatically.

    To provide own modules/classes, add paths to Python files or Python packages
    into the REZZURECT_ENVIRONMENT_MODULES environment variable.

    Args:
        package (str):
            The name of the Rez package to install.
        version (str):
            The specific install of `package`.
        source_path (str):
            The absolute path to the package definition folder.
        build_path (str):
            The absolute path to the package definition's build folder.
        install_path (str):
            The absolute path to where the package's contents will be installed to.
        system (`str`, optional):
            The name of the OS (example: "Linux", "Windows", etc.)
            If nothing is given, the user's current system is used, instead.
        distribution (`str`, optional):
            The name of the type of OS (example: "CentOS", "windows", etc.)
            If nothing is given, the user's current distribution is used, instead.
        architecture (`str`, optional):
            The explicit name of the architecture. (Example: "x86_64", "AMD64", etc.)
            If nothing is given, the user's current architecture is used, instead.

    '''
    for handler in _get_handlers():
        handler(
            source_path,
            build_path,
            install_path,
            system=system,
            distribution=distribution,
            architecture=architecture,
        )

    adapter = chooser.get_adapter(
        package,
        version,
        system,
        architecture=architecture,
    )

    add_local_filesystem_build(adapter, source_path, install_path)

    add_link_build(adapter)

    return adapter


def add_link_build(adapter):
    '''Add the command which lets the user link Rez to an existing install.

    Args:
        adapter (`rezzurect.adapters.common.BaseAdapter`):
            The object which is used to search for existing installs.

    Raises:
        RuntimeError: If no valid executable could be found.

    '''
    def _skip_build_if_installed(adapter):
        '''Raise a RuntimeError unless `adapter` finds an executable file it can use.'''
        paths = adapter.get_preinstalled_executables()

        for path in paths:
            if os.path.isfile(path):
                return

        raise RuntimeError('No expected binary file could be found. '
                           'Checked "{paths}".'.format(paths=', '.join(sorted(paths))))

    strategy.register_strategy(
        'link',
        functools.partial(_skip_build_if_installed, adapter),
    )


def add_local_filesystem_build(adapter, source_path, install_path):
    '''Search the user's files and build the Rez package.

    Args:
        adapter (`rezzurect.adapters.common.BaseAdapter`):
            The object which is used to "install" the files.
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.

    '''
    strategy.register_strategy(
        'local',
        functools.partial(_make_install_and_install_with_local, adapter, source_path, install_path),
        priority=True,
    )


def add_ftp_filesystem_build(adapter, source_path, install_path):
    '''Download the files from FTP and the Rez package if needed.

    Args:
        adapter (`rezzurect.adapters.common.BaseAdapter`):
            The object which is used to "install" the files from FTP.
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.

    '''
    def _make_install_and_install_with_ftp(adapter, source_path, install_path):
        if not os.path.isdir(install_path):
            os.makedirs(install_path)

        server = os.environ['REZZURECT_FTP_SERVER']

        adapter.install_from_ftp(server, source_path, install_path)

    strategy.register_strategy(
        'ftp',
        functools.partial(_make_install_and_install_with_local, adapter, source_path, install_path),
        priority=True,
    )



# TODO : Consider removing `install_path` since a module definition might be easier to work with
def init(
        package,
        version,
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    '''Load all of the user's defined build methods.

    If no build methods were specified, a set of default build methods are
    sourced by rezzurect, automatically.

    To provide own modules/classes, add paths to Python files or Python packages
    into the REZZURECT_ENVIRONMENT_MODULES environment variable.

    Args:
        package (str):
            The name of the Rez package to install.
        version (str):
            The specific install of `package`.
        source_path (str):
            The absolute path to the package definition folder.
        build_path (str):
            The absolute path to the package definition's build folder.
        install_path (str):
            The absolute path to where the package's contents will be installed to.
        system (`str`, optional):
            The name of the OS (example: "Linux", "Windows", etc.)
            If nothing is given, the user's current system is used, instead.
        distribution (`str`, optional):
            The name of the type of OS (example: "CentOS", "windows", etc.)
            If nothing is given, the user's current distribution is used, instead.
        architecture (`str`, optional):
            The explicit name of the architecture. (Example: "x86_64", "AMD64", etc.)
            If nothing is given, the user's current architecture is used, instead.

    '''
    if not system or not distribution or not architecture:
        system_, distribution_, architecture_ = _get_rez_environment_details()

        if not system:
            system = system_

        if not distribution:
            distribution = distribution_

        if not architecture:
            architecture = architecture_

    return _init(
        package,
        version,
        source_path,
        build_path,
        install_path,
        system,
        distribution,
        architecture,
    )
