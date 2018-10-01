#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module that manages rezzurect and how it gets distributed to Rez packages.'''

# IMPORT STANDARD LIBRARIES
from distutils import dir_util
import os

# IMPORT THIRD-PARTY LIBRARIES
import rezzurect


def copy_rezzurect_to(path):
    '''Copy rezzurect into the given directory.

    rezzurect needs to be available for import when a package is executed so
    this function should be run (ideally always but only) once on-build.

    Args:
        path (str): The absolute path to a package's python folder.

    '''
    root = os.path.dirname(os.path.realpath(rezzurect.__file__))
    name = os.path.basename(root)  # Should always just be 'rezzurect'

    if not os.path.isdir(path):
        os.makedirs(path)

    destination = os.path.join(path, name)
    dir_util.copy_tree(root, destination)
