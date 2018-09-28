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
from .build_adapters import build_adapter
from .build_adapters import git_remote
from .build_adapters import internet
from .build_adapters import strategy
from . import common


def _get_rez_environment_details():
    # TODO : There has to be a better way to query this info. Find out, later
    request = re.compile(r'~(\w+)==(\w+)')

    output = {key: value for key, value in request.findall(os.environ.get('REZ_REQUEST', ''))}
    platform_ = output['platform'].capitalize()
    return (platform_, output['os'], output['arch'])


def _init(
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    add_from_internet(source_path, system, distribution, architecture)

    add_git_remote_search(build_path, system.lower(), distribution, architecture)

    adapter = build_adapter.get_adapter(system, architecture=architecture)
    add_local_filesystem_search(adapter, source_path, install_path)

    return adapter


def add_git_remote_search(build_path, system, distribution, architecture):
    git_command = git_remote.get_git_command(
        git_remote.get_git_root_url(os.path.dirname(build_path)),
        system.lower(),
        distribution,
        architecture,
    )
    strategy.register_strategy('git', git_command)


def add_git_remote_ssh(install_path, system, distribution, architecture):
    git_command = git_remote.get_git_command(
        # TODO : This URL needs to be "resolved" properly
        'selecaotwo@192.168.0.11:/srv/git/rez-nuke.git',
        path=install_path,
        system=system,
        distribution=distribution,
        architecture=architecture,
    )
    strategy.register_strategy('git-ssh', git_command)


def add_local_filesystem_search(adapter, source_path, install_path):
    strategy.register_strategy(
        'local',
        functools.partial(adapter.get_from_local, source_path, install_path),
        priority=True,
    )


def add_from_internet(package, system, distribution, architecture):
    download_from_package = functools.partial(
        internet.download,
        package,
        system,
        distribution,
        architecture,
    )
    strategy.register_strategy('download', download_from_package)


def get_package_name(path):
    for root in config.config.packages_path:
        package = os.path.relpath(path, root)

        found = not package.startswith('.')

        if found:
            # TODO : Make a better split function, later
            return package.split(os.sep)[0]

    return ''


def init(source_path, build_path, install_path):
    system, distribution, architecture = _get_rez_environment_details()
    return _init(source_path, build_path, install_path, system, distribution, architecture)
