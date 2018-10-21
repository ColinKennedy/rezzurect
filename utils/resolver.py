#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import os

# IMPORT THIRD-PARTY LIBRARIES
from yaml import parser
import json
import yaml


# TODO : Add this function to a rez-related module
def get_pipeline_configuration_root():
    raise NotImplementedError('Need to write this')


# TODO : Replace this with a rez-related module function
_PIPELINE_CONFIGURATION_ROOT = get_pipeline_configuration_root()
# _PIPELINE_CONFIGURATION_ROOT = rez_helper.get_pipeline_configuration_root()


def _read_setting_file(path):
    def _as_json(path):
        with open(path, 'r') as file_:
            return json.load(file_)

    def _as_yaml(path):
        with open(path, 'r') as file_:
            return yaml.safe_load(file_)

    known_exceptions = (
        # If the JSON has syntax issues
        ValueError,

        # If the YAML has syntax issues
        parser.ParserError,
    )

    for loader in (_as_yaml, _as_json):
        try:
            return loader(path)
        except known_exceptions:
            pass

    return dict()


def _read_settings_from_shotgun_field():
    raise NotImplementedError('Need to write this, too')


def _read_all_respawnrc_settings():
    output = dict()

    # TODO : Need to get Shotgun settings to find out where the Pipeline
    #        Configuration root is
    #
    configuration_setting_file = os.path.join(_PIPELINE_CONFIGURATION_ROOT, '.respawnrc')

    if os.path.file(configuration_setting_file):
        output.update(_read_setting_file(configuration_setting_file))

    output.update(_read_settings_from_shotgun_field())
    output.update(_read_setting_file(os.path.expanduser('~/.respawnrc')))

    return output


def expand(text):
    settings = _read_all_respawnrc_settings()
    settings['respawn_root'] = _PIPELINE_CONFIGURATION_ROOT

    return text.format(**settings)
