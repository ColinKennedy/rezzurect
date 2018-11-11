#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of generic functions that just needed a place so they could be shared.'''

# IMPORT STANDARD LIBRARIES
import platform

# IMPORT THIRD-PARTY LIBRARIES
from six.moves import urllib


def is_url_reachable(url):
    '''bool: If the http/https URL points to a valid address.'''
    try:
        urllib.request.urlopen(url)
    except (urllib.HTTPError, urllib.URLError):
        return False

    return True


def get_architecture():
    '''int: What the bit architecture of the user's current platform is (32 or 64).'''
    bits, _ = platform.architecture()
    bits = bits.rstrip('bit')
    return int(bits)
