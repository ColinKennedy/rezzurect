#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main configuration that is shared across all Respawn-related modules.

For example, the "rez_packages" submodule uses this module to determine where
installed files will go to. Also, this module is responsible for setting up the
"RESPAWN_PYTHONPATH" environment variable. "RESPAWN_PYTHONPATH" is needed by
Rez packages in order to find rezzurect and other helper modules whenever Rez
is building or entering a package.

`init_custom_pythonpath` is used to link the user's Shotgun session (again,
using "RESPAWN_PYTHONPATH") to the Rez packages that it will build or run.

'''

# IMPORT STANDARD LIBRARIES
import sys
import os

# IMPORT LOCAL LIBRARIES
from . import _rezzurect_config


INSTALL_FOLDER_NAME = 'install'
REZ_PACKAGE_ROOT_FOLDER = _rezzurect_config.get_root_package_folder()


def init_custom_pythonpath():
    '''Add paths that Respawn needs to import packages to the user's session.'''
    current_dir = os.path.dirname(os.path.realpath(__file__))

    vendors_directory = os.path.dirname(os.path.dirname(current_dir))
    rez_python_package_directory = os.path.join(vendors_directory, 'rez-2.23.1-py2.7')
    managed_paths = [vendors_directory, rez_python_package_directory]

    sys.path.extend(managed_paths)
    os.environ['RESPAWN_PYTHONPATH'] = (os.pathsep).join(managed_paths)
