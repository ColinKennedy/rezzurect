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
import json
import sys
import os
import re

# IMPORT THIRD-PARTY LIBRARIES
from yaml import parser
import yaml
import six

# IMPORT LOCAL LIBRARIES
from . import multipurpose_helper


_ENVIRONMENT_EXPRESSION = re.compile(r'REZZURECT_CUSTOM_KEY_(?P<key>\w+)')
INSTALL_FOLDER_NAME = 'install'
PIPELINE_CONFIGURATION_ROOT = multipurpose_helper.get_current_pipeline_configuration_root_safe()


def _read_setting_file(path):
    '''dict[str, str]: Try to read the given file as a JSON or YAML file.'''
    def _as_json(path):
        with open(path, 'r') as file_:
            return json.load(file_)

    def _as_yaml(path):
        with open(path, 'r') as file_:
            return yaml.safe_load(file_)

    known_exceptions = (
        # If the file does not exist
        IOError,

        # If the JSON has syntax issues
        ValueError,

        # If the YAML has syntax issues
        parser.ParserError,
    )

    for loader in (_as_yaml, _as_json):
        try:
            return loader(path) or dict()
        except known_exceptions:
            pass

    return dict()


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


def get_environment_variables():
    output = dict()

    if 'RESPAWN_REZ_PACKAGE_ROOT' in os.environ:
        output['rez_package_root'] = os.environ['RESPAWN_REZ_PACKAGE_ROOT']

    if 'RESPAWN_AUTO_INSTALLS' in os.environ:
        output['auto_installs'] = os.environ['RESPAWN_AUTO_INSTALLS'] == '1'

    return output


def get_custom_keys_from_environment():
    '''dict[str, str]: Get every user-defined custom key and its value.'''
    keys = dict()

    for key, value in six.iteritems(os.environ):
        match = _ENVIRONMENT_EXPRESSION.match(key)

        if match:
            keys[match.group('key')] = value

    return keys


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

    rez_package_folder = get_settings().get('rez_package_root', '')
    if rez_package_folder:
        return rez_package_folder

    configuration_root = multipurpose_helper.get_current_pipeline_configuration_root_safe()

    if not configuration_root:
        # We can't get the configuration directory from Shotgun so, as a last resort,
        # we will look up this directory to find the "rez_packages" folder
        #
        configuration_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    return os.path.join(configuration_root, 'rez_packages')


def get_settings():
    '''dict[str, str]: All of the user-defined Respawn custom keys.'''
    def update(data, output):
        for key, value in data.items():
            if key == 'keys':
                output[key].update(value)
            else:
                output[key] = value

    output = {
        'keys': dict(),
    }

    update(read_configuration_setting_file(), output)
    update(multipurpose_helper.read_settings_from_shotgun_field_safe(), output)
    update(read_user_settings_file(), output)
    update({'keys': get_custom_keys_from_environment()}, output)
    update(get_environment_variables(), output)

    output['respawn_root'] = PIPELINE_CONFIGURATION_ROOT

    return output


def read_configuration_setting_file():
    '''dict[str, str]: Get the custom keys for this Configuration.'''
    if not os.path.isdir(PIPELINE_CONFIGURATION_ROOT):
        return dict()

    settings_file = os.path.join(PIPELINE_CONFIGURATION_ROOT, '.respawnrc')

    if not os.path.isfile(settings_file):
        return dict()

    return _read_setting_file(settings_file)


def read_user_settings_file():
    '''dict[str, str]: Get every user-defined custom key.'''
    settings_file = os.path.expanduser('~/.respawnrc')

    if not os.path.isfile(settings_file):
        return dict()

    return _read_setting_file(settings_file)
