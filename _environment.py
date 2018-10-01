#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which loads some pre-defined methods to build Rez packages.'''

# IMPORT STANDARD LIBRARIES
import functools
import platform
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez import config

# IMPORT LOCAL LIBRARIES
from .build_adapters import git_remote
from .build_adapters import internet
from .build_adapters import strategy
from . import common


def add_from_internet_build(package, system, distribution, architecture):
    '''Add a function which download the package's required files and install them.

    Args:
        package (str): The name of the package to install.
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str): The name of the type of OS (Example: "CentOS", "windows", etc.)

    '''
    download_from_package = functools.partial(
        internet.download,
        package,
        system,
        distribution,
        architecture,
    )
    strategy.register_strategy('download', download_from_package)


def add_git_remote_build(build_path, system, distribution, architecture):
    '''Add a function which download the package's required files and install them.

    Args:
        build_path (str): The absolute path to the Rez package's build folder.
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str): The name of the type of OS (Example: "CentOS", "windows", etc.)

    '''
    git_command = git_remote.get_git_command(
        git_remote.get_git_root_url(os.path.dirname(build_path)),
        system.lower(),
        distribution,
        architecture,
    )
    strategy.register_strategy('git', git_command)


def add_git_remote_ssh_build(install_path, system, distribution, architecture):
    '''Find a git repository through SSH and clone it to the user's directory.

    Args:
        install_path (str): The absolute path to where the git repo will be cloned to.
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str): The name of the type of OS (Example: "CentOS", "windows", etc.)

    '''
    git_command = git_remote.get_git_command(
        # TODO : This URL needs to be "resolved" properly
        'selecaotwo@192.168.0.11:/srv/git/rez-nuke.git',
        path=install_path,
        system=system,
        distribution=distribution,
        architecture=architecture,
    )
    strategy.register_strategy('git-ssh', git_command)


# TODO : This function, `get_package_name`, is probably not necessary.
#        Look into how to get the package name on-build and then remove this, later
#
def get_package_name(path):
    '''Get the name of the rez package that is being operated on.

    Args:
        path (str): The absolute path to the build path of some rez package.

    Returns:
        str: The found name, if any.

    '''
    for root in config.config.packages_path:
        package = os.path.relpath(path, root)

        found = not package.startswith('.')

        if found:
            # TODO : Make a better split function, later
            return package.split(os.sep)[0]

    return ''


def main(
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    '''Load all of the user's defined build methods.

    The currently supported build methods are:

        git-ssh
        local (filesystem)

    Args:
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
    package_name = get_package_name(source_path)
    add_from_internet(package_name, system, distribution, architecture)

    add_git_remote_ssh(install_path, system, distribution, architecture)

    add_git_remote_search(build_path, system.lower(), distribution, architecture)
