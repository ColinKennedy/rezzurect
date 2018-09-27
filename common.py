#!/usr/bin/env python
#

# IMPORT STANDARD LIBRARIES
import platform
import urllib2


def is_url_reachable(url):
    url, _ = split_url(url)

    try:
        urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError):
        return False

    return True


def get_architecture():
    bits, _ = platform.architecture()
    bits = bits.rstrip('bit')
    return int(bits)


def split_url(url):
    ending = '.git'
    if url.endswith(ending):
        return (url[:-1 * len(ending)], ending)

    return (url, '')
