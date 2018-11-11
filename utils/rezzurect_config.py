#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main configuration that is shared across all Respawn-related modules.

For example, the "rez_packages" submodule uses this module to determine where
installed files will go to. Also, this module is responsible for setting up the
"RESPAWN_PYTHONPATH" environment variable. "RESPAWN_PYTHONPATH" is needed by
Rez packages in order to find rezzurect and other helper modules whenever Rez
is building or entering a package.

`init_custom_pythonpath` is used to link the user's Shotgun session (again,
using `RESPAWN_PYTHONPATH`) to the Rez packages that it will build or run.

'''

# IMPORT STANDARD LIBRARIES
import sys
import os

# IMPORT LOCAL LIBRARIES
import _rezzurect_config


INSTALL_FOLDER_NAME = 'install'
REZ_PACKAGE_ROOT_FOLDER = _rezzurect_config.get_root_package_folder()


def init_custom_pythonpath():
    '''Add paths that Respawn needs to import packages to the user's session.

    Important:
        If the user has already defined the `REZZURECT_LOCATION`
        environment variable then we will just use that, instead.

    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    vendors_directory = os.path.dirname(os.path.dirname(current_dir))

    rezzurect_location = os.getenv('REZZURECT_LOCATION', '')

    if not rezzurect_location:
        rezzurect_location = vendors_directory

    rez_python_package_directory = os.path.join(vendors_directory, 'rez-2.23.1-py2.7')

    sys.path.append(rezzurect_location)
    sys.path.append(rez_python_package_directory)

    os.environ['REZZURECT_LOCATION'] = rezzurect_location
    os.environ['RESPAWN_PYTHONPATH'] = rez_python_package_directory
