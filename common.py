#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of generic functions that just needed a place so they could be shared.'''

# IMPORT STANDARD LIBRARIES
import platform
import urllib2


def is_url_reachable(url):
    '''bool: If the http/https URL points to a valid address.'''
    try:
        urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError):
        return False

    return True


def get_architecture():
    '''int: What the bit architecture of the user's current platform is (32 or 64).'''
    bits, _ = platform.architecture()
    bits = bits.rstrip('bit')
    return int(bits)
