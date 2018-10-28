#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A companion module to `rezzurect_config`.

This module is basically just a place to put functions that would otherwise
make `rezzurect_config` harder to read. This module doesn't have any special
meaning other than that.

'''

# IMPORT STANDARD LIBRARIES
import os

# IMPORT LOCAL LIBRARIES
from . import multipurpose_helper
from . import resolver


def get_root_package_folder():
    '''Get the location of the user's Rez packages, on-disk.

    Check #1:
        If the user has the "RESPAWN_REZ_PACKAGE_ROOT" environment variable defined
        then use it.

    Check #2:
        Look for this pipeline configuration's .respawnrc file.
        If a key called "rez_package_root" is defined, use it.

    Check #3:
        Look for the user's "~/.respawnrc" file.
        If a key called "rez_package_root" is defined, use it.

    Check #4:
        Otherwise, try to get the configuration's "rez_packages" folder, instead.

    Returns:
        str: The absolute path to a folder where Rez packages can be found.

    '''
    rez_package_folder = os.getenv('RESPAWN_REZ_PACKAGE_ROOT', '')
    if rez_package_folder:
        return rez_package_folder

    rez_package_folder = resolver.get_settings().get('rez_package_root', '')
    if rez_package_folder:
        return rez_package_folder

    configuration_root = multipurpose_helper.get_current_pipeline_configuration_root_safe()

    if not configuration_root:
        # We can't get the configuration directory from Shotgun so, as a last resort,
        # we will look up this directory to find the "rez_packages" folder
        #
        configuration_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    return os.path.join(configuration_root, 'rez_packages')
