#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import functools
import platform
import os
import re


# IMPORT THIRD-PARTY LIBRARIES
from rez import config


# IMPORT LOCAL LIBRARIES
from . import environment_git
from . import build_adapter
from . import strategy
from . import common


def _get_rez_environment_details():
    # TODO : There has to be a better way to query this info. Find out, later
    request = re.compile('~(\w+)==(\w+)')

    output = {key: value for key, value in request.findall(os.environ.get('REZ_REQUEST', ''))}
    platform_ = output['platform'].capitalize()
    return (platform_, output['os'], output['arch'])


def _init(
        source_path,
        build_path,
        install_path,
        platform=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    adapter = build_adapter.get_adapter(platform, architecture=architecture)

    # Try the local filesystem
    strategy.register_strategy(
        'local',
        functools.partial(adapter.get_from_local, source_path, install_path),
        priority=True,
    )

    # Try to download from the internet
    download_from_package = functools.partial(
        internet.download,
        get_package_name(source_path),
        platform,
        distribution,
        architecture,
    )
    strategy.register_strategy(
        'download',
        download_from_package,
    )

    # Try to download from git
    git_command = environment_git.get_git_command(
        environment_git.get_git_root_url(os.path.dirname(build_path)),
        platform.lower(),
        distribution,
        architecture,
    )
    strategy.register_strategy('git', git_command)

    return adapter


def get_package_name(path):
    for root in config.config.packages_path:
        package = os.path.relpath(path, root)

        found = not package.startswith('.')

        if found:
            # TODO : Make a better split function, later
            return package.split(os.sep)[0]

    return ''


def init(source_path, build_path, install_path):
    platform, distribution, architecture = _get_rez_environment_details()
    return _init(source_path, build_path, install_path, platform, distribution, architecture)
