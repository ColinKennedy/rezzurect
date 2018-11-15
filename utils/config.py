#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import tempfile
import os

# IMPORT LOCAL LIBRARIES
from . import config_helper as _config_helper


__SETTINGS = _config_helper.get_settings()

AUTO_INSTALLS = __SETTINGS.get('auto_installs', True)

CUSTOM_KEYS = __SETTINGS.get('keys', dict())

INTERNET_DOWNLOADS = __SETTINGS.get('internet_downloads', True)

REZZURECT_LOG_PATH = __SETTINGS.get('rezzurect_log_path', os.path.join(tempfile.gettempdir(), '.rezzurect'))

REZ_PACKAGE_ROOT = _config_helper.get_root_package_folder()

STRATEGY_ORDERS = __SETTINGS.get('strategy_orders', dict())


def recalculate():
    global AUTO_INSTALLS
    global CUSTOM_KEYS
    global INTERNET_DOWNLOADS
    global REZZURECT_LOG_PATH
    global REZ_PACKAGE_ROOT
    global STRATEGY_ORDERS

    settings = _config_helper.get_settings()

    AUTO_INSTALLS = settings.get('auto_installs', True)

    CUSTOM_KEYS = settings.get('keys', dict())

    INTERNET_DOWNLOADS = settings.get('internet_downloads', True)

    REZZURECT_LOG_PATH = settings.get('rezzurect_log_path', os.path.join(tempfile.gettempdir(), '.rezzurect'))

    REZ_PACKAGE_ROOT = _config_helper.get_root_package_folder()

    STRATEGY_ORDERS = settings.get('strategy_orders', dict())
