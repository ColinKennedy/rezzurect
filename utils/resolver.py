#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import logging
import os

# IMPORT THIRD-PARTY LIBRARIES
from yaml import parser
import json
import yaml


LOGGER = logging.getLogger('rezzurect.config')


# TODO : Add this function to a rez-related module
def get_current_pipeline_configuration():
    from sgtk import pipelineconfig_factory
    return pipelineconfig_factory.from_path(os.getenv('TANK_CURRENT_PC'))


def get_current_pipeline_configuration_safe():
    try:
        return get_current_pipeline_configuration()
    except ImportError:
        return None


def get_current_pipeline_configuration_root():
    return get_current_pipeline_configuration().get_config_location()


def get_current_pipeline_configuration_root_safe():
    try:
        return get_current_pipeline_configuration_root()
    except ImportError:
        return ''


try:
    # TODO : Replace this with a rez-related module function
    _PIPELINE_CONFIGURATION_ROOT = get_current_pipeline_configuration_root_safe()
except ImportError:
    # This happens if a rez package was called from command-line with no Shotgun Context
    _PIPELINE_CONFIGURATION_ROOT = ''


def _read_setting_file(path):
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


def _read_settings_from_shotgun_field():
    from sgtk import authentication
    authenticator = authentication.ShotgunAuthenticator()
    user = authenticator.get_user()
    sg = user.create_sg_connection()

    try:
        has_respawn_key_field = bool(sg.schema_field_read('PipelineConfiguration', 'sg_respawn_keys'))
    except Exception:  # TODO : Replace with `shotgun.Fault`
        has_respawn_key_field = False

    if not has_respawn_key_field:
        return dict()

    configuration_id = get_current_pipeline_configuration().get_shotgun_id()
    configuration = sg.find_one(
        'PipelineConfiguration',
        [['id', 'is', configuration_id]],
        ['sg_respawn_keys'],
    )

    return json.loads(configuration.get('sg_respawn_keys', ''))


def _read_settings_from_shotgun_field_safe():
    try:
        return _read_settings_from_shotgun_field()
    except (ImportError, TypeError):
        LOGGER.exception('Respawn Shotgun Field field was not found or has a syntax error.')

        configuration = get_current_pipeline_configuration_safe()

        if configuration:
            LOGGER.debug(
                'Configuration name "%s" and id "%s" has missing field.',
                configuration.get_project_disk_name(),
                configuration.get_shotgun_id(),
            )
        else:
            LOGGER.debug('No configuration was found.')

        return dict()


def _read_all_respawnrc_settings():
    output = dict()

    configuration_setting_file = os.path.join(_PIPELINE_CONFIGURATION_ROOT, '.respawnrc')

    if os.path.isfile(configuration_setting_file):
        output.update(_read_setting_file(configuration_setting_file))

    output.update(_read_settings_from_shotgun_field_safe())
    output.update(_read_setting_file(os.path.expanduser('~/.respawnrc')))

    return output


def expand(text):
    settings = _read_all_respawnrc_settings()
    settings['respawn_root'] = _PIPELINE_CONFIGURATION_ROOT

    try:
        return text.format(**settings)
    except KeyError:
        LOGGER.exception(
            'Text "%s" is missing one or more keys. Keys found, "%s".', text, settings)
        raise
