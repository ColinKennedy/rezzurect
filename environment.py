#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import functools
import platform
import os
import re

# IMPORT LOCAL LIBRARIES
from .build_adapters import build_adapter
from .build_adapters import strategy
from . import common


def _get_rez_environment_details():
    # TODO : There has to be a better way to query this info. Find out, later
    request = re.compile(r'~(\w+)==(\w+)')

    output = {key: value for key, value in request.findall(os.environ.get('REZ_REQUEST', ''))}
    platform_ = output['platform'].capitalize()
    return (platform_, output['os'], output['arch'])


def _resolve_module(path):
    if os.path.isabs(path):
        try:
            return imp.load_source('', path)
        except ImportError:
            return

    try:
        module = __import__(path)
    except ImportError:
        return
    else:
        modules = path.split('.')
        item = module

        for index in range(1, len(modules)):
            item = getattr(item, modules[index])

        return item


def _init(
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    modules = os.getenv('REZZURECT_ENVIRONMENT_MODULES', '')

    paths = ['rezzurect._environment']
    if modules:
        paths = []

        for module in modules:
            module = module.strip()

            if module:
                paths.append(module)

    for path in paths:
        module = _resolve_module(path)

        if not module:
            continue

        module.main(
            source_path,
            build_path,
            install_path,
            system=system,
            distribution=distribution,
            architecture=architecture,
        )

    adapter = build_adapter.get_adapter(system, architecture=architecture)
    add_local_filesystem_search(adapter, source_path, install_path)

    return adapter


def add_local_filesystem_search(adapter, source_path, install_path):
    strategy.register_strategy(
        'local',
        functools.partial(adapter.get_from_local, source_path, install_path),
        priority=True,
    )


def init(source_path, build_path, install_path):
    system, distribution, architecture = _get_rez_environment_details()
    return _init(source_path, build_path, install_path, system, distribution, architecture)
