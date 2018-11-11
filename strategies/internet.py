#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of functions for downloading executable files over the Internet.'''

# IMPORT STANDARD LIBRARIES
import logging
import os

# IMPORT LOCAL LIBRARIES
from ..utils import progressbar
from ..utils import common
from ..vendors import six


_LOGGER = logging.getLogger('rezzurect.internet')


def _get_url(package, version, system, architecture):
    '''Find the URL for the package and system and return it.

    Args:
        package (str): The name of the package to get a URL for. Example: "houdini".
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

    Returns:
        str: The found URL, if any.

    '''
    # TODO : Move this to a config file somewhere else
    nuke_root = 'https://www.foundry.com/products/download_product?file='
    houdini_ftp_165 = 'ftp://ftp.sidefx.com/public/Houdini16.5/Build.536'

    references = {
        ('houdini', '16.5.536', 'Linux', 64):
            '{0}/houdini-16.5.536-linux_x86_64_gcc4.8.tar.gz'.format(houdini_ftp_165),
        # TODO : Re-add this once SideFX gets back to me. Ticket ID "SESI #67857"
        # ('houdini', '17.0.352', 'Linux', 64):
        #     'https://www.sidefx.com/download/download-houdini/55041/get',
        ('nuke', '11.2v3', 'Linux', 64):
            '{nuke_root}Nuke11.2v3-linux-x86-release-64.tgz'.format(nuke_root=nuke_root),
        ('nuke', '10.5v8', 'Linux', 64):
            '{nuke_root}Nuke10.5v8-linux-x86-release-64.tgz'.format(nuke_root=nuke_root),
        ('nuke', '11.2v3', 'Windows', 64):
            '{nuke_root}Nuke11.2v3-win-x86-release-64.zip'.format(nuke_root=nuke_root),
        ('nuke', '10.5v8', 'Windows', 64):
            '{nuke_root}Nuke10.5v8-win-x86-release-64.zip'.format(nuke_root=nuke_root),
    }

    option = (package, version, system, architecture)

    _LOGGER.trace('Checking for URL using "%s".', option)

    try:
        url = references[option]
    except KeyError:
        return ''

    if common.is_url_reachable(url):
        return url

    return ''


def _install_from_url(url, destination):
    '''Download the contents of the URL to some location on-disk.

    Args:
        url (str): The Internet address to download from.
        destination (str): The location where the package's files should download to.

    Raises:
        RuntimeError: If the Internet download is interrupted (by the user or
                      by the Internet connection).

    '''
    try:
        six.moves.urllib.request.urlretrieve(
            url,
            destination,
            reporthook=progressbar.UrllibProgress(_LOGGER.trace).download_progress_hook,
        )
    except six.moves.urllib.ContentTooShortError:
        # Reference: https://docs.python.org/2/library/urllib.html#urllib.ContentTooShortError
        # "This can occur, for example, when the download is interrupted."
        #
        raise RuntimeError('Download was interrupted')


def get_recommended_file_name(url):
    '''Find the filename for the given download URL.

    Args:
        url (str): The address which points to some file on a remote server.
                   Example: "https://www.example/foo/bar.zip"`

    Returns:
        str: The recommended name, if any.

    '''
    _, _, path, query, _ = six.moves.urlparse.urlsplit(url)

    # Example:
    # url='https://www.foundry.com/products/download_product?file=Nuke10.5v8-win-x86-release-64.zip'
    # query='file=Nuke10.5v8-win-x86-release-64.zip'
    #
    if query:
        return url.split('=')[-1]

    # Example:
    # `url = 'https://www.example/foo/bar.zip'`
    # `query = '/foo/bar.zip'`
    #
    return path.split('/')[-1]


def download(package, version, system, architecture, destination):
    '''Download a package from online, using http/https.

    Args:
        package (str): The name of the package to get a URL for. Example: "houdini".
        version (str): The specific version of `package` to download.
        system (str): The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.
        destination (str): The location where the package's files should download to.

    Raises:
        RuntimeError: If no URL for the given settings could be found
                      or if a filename for the given URL could be found.

    '''
    url = _get_url(package, version, system, architecture)

    if not url:
        raise RuntimeError('No URL could be found for "{data}".'.format(
            data=(package, version, system, architecture)))

    file_name = get_recommended_file_name(url)

    if not file_name:
        raise RuntimeError('No filename could be found for "{url}".'.format(url=url))

    destination = os.path.join(destination, file_name)
    _install_from_url(url, destination)

    return destination
