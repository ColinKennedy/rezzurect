#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which is used to communicate with paths outside of Rezzurect.

Reference:
    https://github.com/ColinKennedy/tk-config-default2-respawn/wiki/Referring-To-Custom-Code

'''

# IMPORT STANDARD LIBRARIES
import logging
import os

# IMPORT THIRD-PARTY LIBRARIES
from yaml import parser
import json
import yaml

# IMPORT LOCAL LIBRARIES
from . import helper


LOGGER = logging.getLogger('rezzurect.config')
_PIPELINE_CONFIGURATION_ROOT = helper.get_current_pipeline_configuration_root_safe()


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


def _read_all_respawnrc_settings():
    '''dict[str, str]: All of the user-defined Respawn environment keys.'''
    output = dict()

    configuration_setting_file = os.path.join(_PIPELINE_CONFIGURATION_ROOT, '.respawnrc')

    if os.path.isfile(configuration_setting_file):
        output.update(_read_setting_file(configuration_setting_file))

    output.update(helper.read_settings_from_shotgun_field_safe())
    output.update(_read_setting_file(os.path.expanduser('~/.respawnrc')))

    return output


def expand(text):
    '''Replace the given format text with an absolute path.

    Important:
        The keys which are used to expand `text` come from
        the user's environment settings. The only "reserved" key that the user
        may not modify is "respawn_root", which signifies the current path to
        the user's current Pipeline Configuration.

    Args:
        text (str): Some Python string to expand such as "{foo}/bar".

    Returns:
        str: The expanded text result.

    '''
    settings = _read_all_respawnrc_settings()
    settings['respawn_root'] = _PIPELINE_CONFIGURATION_ROOT

    try:
        return text.format(**settings)
    except KeyError:
        LOGGER.exception(
            'Text "%s" is missing one or more keys. Keys found, "%s".', text, settings)
        raise
