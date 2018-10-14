#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which loads some "off-the-shelf" functions which build Rez packages.

This module is loaded by `rezzurect.environment`. It's not required for rezzurect
to work but the adapters that this module initializes must be replaced or
rezzurect will fail to build / source / run Rez packages correctly.

'''

# IMPORT STANDARD LIBRARIES
import platform

# IMPORT LOCAL LIBRARIES
from .adapters.nuke import nuke_builder
from .utils import common


# TODO : Possibly get rid of `build_path`
def main(
        source_path,
        build_path,
        install_path,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
):
    '''Load all of the user's defined build methods.

    Args:
        source_path (str):
            The absolute path to the package definition folder.
            Example: "$USER/configs/tk-config-default2/rez_packages/nuke/10.5v8".
        build_path (str):
            The absolute path to the package definition's build folder.
            Example: "$USER/configs/tk-config-default2/rez_packages/nuke/10.5v8/build".
        install_path (str):
            The absolute path to where the package's contents will be installed to.
            Example: "$USER/packages/nuke/10.5v8/install"
        system (`str`, optional):
            The name of the OS (example: "Linux", "Windows", etc.)
            If nothing is given, the user's current system is used, instead.
        distribution (`str`, optional):
            The name of the type of OS (example: "CentOS", "windows", etc.)
            If nothing is given, the user's current distribution is used, instead.
        architecture (`str or int`, optional):
            The explicit name of the architecture. (Example: "x86_64", "AMD64", etc.)
            If nothing is given, the user's current architecture is used, instead.

    '''
    known_modules = (
        nuke_builder,
    )

    # TODO : Replace all these args with a single "EnvironmentContext"
    #        so that each register command can use or ignore parts of a context
    #
    for module in known_modules:
        module.register(
            source_path,
            install_path,
            system,
            distribution,
            architecture,
        )
