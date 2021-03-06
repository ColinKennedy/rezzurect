#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module which is used to initialize Rez-build options.'''

# IMPORT STANDARD LIBRARIES
import platform
import logging
import imp
import os
import re

# IMPORT LOCAL LIBRARIES
from .utils import common
from .utils import logger


LOGGER = logging.getLogger('rezzurect.environment')


def _get_rez_environment_details():
    # TODO : There has to be a better way to query this info. Find out, later
    request = re.compile(r'~(\w+)==(\w+)')

    output = {key: value for key, value in request.findall(os.environ.get('REZ_REQUEST', ''))}
    platform_ = output['platform'].capitalize()
    return (platform_, output['arch'])


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
        return imp.load_source('', path)

    module = __import__(path)
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
        try:
            module = _resolve_object(path)
        except ImportError:
            LOGGER.exception('Path "%s" is not a valid Python module import path.', path)
            continue

        handlers.append(module.main)

    return handlers


# TODO : Consider removing `install_path` since a module definition might be easier to work with
# TODO : Consider merging with and `_init` into one function since our code is
#        much simpler now
#
def init(
        source_path,
        install_path,
        system=platform.system(),
        architecture=common.get_architecture(),
    ):
    '''Load all of the user's defined build methods.

    If no build methods were specified, a set of default build methods are
    sourced by rezzurect, automatically.

    To provide own modules/classes, add paths to Python files or Python packages
    into the REZZURECT_ENVIRONMENT_MODULES environment variable.

    Args:
        source_path (str):
            The absolute path to the package definition folder.
        install_path (str):
            The absolute path to where the package's contents will be installed to.
        system (`str`, optional):
            The name of the OS (example: "Linux", "Windows", etc.)
            If nothing is given, the user's current system is used, instead.
        architecture (`str`, optional):
            The explicit name of the architecture. (Example: "x86_64", "AMD64", etc.)
            If nothing is given, the user's current architecture is used, instead.

    '''
    logger.init()

    if not system or not architecture:
        system_, architecture_ = _get_rez_environment_details()

        if not system:
            system = system_

        if not architecture:
            architecture = architecture_

    for handler in _get_handlers():
        handler(
            source_path,
            install_path,
            system=system,
            architecture=architecture,
        )
