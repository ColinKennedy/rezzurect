#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of functions for downloading executable files over the Internet.'''

# IMPORT STANDARD LIBRARIES
import urlparse
import logging
import os

# IMPORT LOCAL LIBRARIES
from ..utils import progressbar
from ..utils import common
from ..vendors import six


_LOGGER = logging.getLogger('rezzurect.internet')


def _get_url(package, version, system, distribution, architecture):
    '''Find the URL for the package and system and return it.

    Args:
        package (str): The name of the package to get a URL for. Example: "houdini".
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str): The name of the type of OS (Example: "CentOS", "windows", etc.)

    Returns:
        str: The found URL, if any.

    '''
    # TODO : Move this to a config file somewhere else
    references = {
        ('nuke', '11.2v3', 'Linux', 64):
            'https://www.foundry.com/products/download_product?file=Nuke11.2v3-linux-x86-release-64.tgz',
        ('nuke', '10.5v8', 'Linux', 64):
            'https://www.foundry.com/products/download_product?file=Nuke10.5v8-linux-x86-release-64.tgz',
        ('nuke', '11.2v3', 'Windows', 64):
            'https://www.foundry.com/products/download_product?file=Nuke11.2v3-win-x86-release-64.zip',
        ('nuke', '10.5v8', 'Windows', 64):
            'https://www.foundry.com/products/download_product?file=Nuke10.5v8-win-x86-release-64.zip',
    }

    option = (package, version, system, architecture)

    _LOGGER.trace('Checking for URL using "%s".', option)

    try:
        url = references[option]
    except KeyError:
        continue

    if common.is_url_reachable(url):
        return url

    return ''


def _install_from_url(url, destination):
    '''Download the contents of the URL to some location on-disk.

    Args:
        url (str): The Internet address to download from.
        destination (str): The location where the package's files should download to.


    '''
    six.moves.urllib.request.urlretrieve(
        url,
        destination,
        reporthook=progressbar.UrllibProgress(_LOGGER.trace).download_progress_hook,
    )


def get_recommended_file_name(url):
    '''Find the filename for the given download URL.

    Args:
        url (str): The address which points to some file on a remote server.
                   Example: "https://www.foundry.com/products/download_product?file=Nuke10.5v8-win-x86-release-64.zip"`
                   Example: "https://www.example/foo/bar.zip"`

    Returns:
        str: The recommended name, if any.

    '''
    _, _, path, query, _ = urlparse.urlsplit(url)

    if query:
        # Example:
        # `url = 'https://www.foundry.com/products/download_product?file=Nuke10.5v8-win-x86-release-64.zip'`
        # `query = 'file=Nuke10.5v8-win-x86-release-64.zip'
        #
        return url.split('=')[-1]

    # Example:
    # `url = 'https://www.example/foo/bar.zip'`
    # `query = '/foo/bar.zip'`
    #
    return path.split('/')[-1]


def download(package, version, system, distribution, architecture, destination):
    '''Download a package from online, using http/https.

    Args:
        package (str): The name of the package to get a URL for. Example: "houdini".
        version (str): The specific version of `package` to download.
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str): The name of the type of OS (Example: "CentOS", "windows", etc.)
        destination (str): The location where the package's files should download to.

    Raises:
        RuntimeError: If no URL for the given settings could be found
                      or if a filename for the given URL could be found.

    '''
    url = _get_url(package, version, system, distribution, architecture)

    if not url:
        raise RuntimeError('No URL could be found for "{data}".'.format(
            data=(package, version, system, distribution, architecture)))

    file_name = get_recommended_file_name(url)

    if not file_name:
        raise RuntimeError('No filename could be found for "{url}".'.format(url=url))

    destination = os.path.join(destination, file_name)
    _install_from_url(url, destination)

    return destination
