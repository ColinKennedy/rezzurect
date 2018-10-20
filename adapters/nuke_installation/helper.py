#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Any information that is used between one or more adapter modules.'''

# IMPORT STANDARD LIBRARIES
import os
import re


VERSION_PARSER = re.compile(r'(?P<major>\d+).(?P<minor>\d+)v(?P<patch>\d+)')


def get_preinstalled_linux_executables(version):
    '''Get a list of possible pre-installed executable Nuke files.

    Args:
        version (str): A version of Nuke. Example: "11.2v3".

    Raises:
        RuntimeError:
            If we can't get version information from the stored version then
            this function will fail. Normally though, assuming this adapter
            was built correctly, this shouldn't occur.

    Returns:
        str: The absolute path to a Nuke executable.

    '''
    major, minor, _ = get_version_parts(version)

    if not major:
        raise RuntimeError(
            'Version "{version}" has no major component. This should not happen.'
            ''.format(version=version))

    if not minor:
        raise RuntimeError(
            'Version "{version}" has no minor component. This should not happen.'
            ''.format(version=version))

    options = [
        '/usr/local/Nuke{version}/Nuke{major}.{minor}',
        os.path.expanduser('~/Nuke{version}/Nuke{major}.{minor}'),
    ]

    return set((path.format(version=version, major=major, minor=minor)
                for path in options))


def get_preinstalled_windows_executables(version):
    '''Get a list of possible pre-installed executable Nuke files.

    Args:
        version (str): A version of Nuke. Example: "11.2v3".

    Raises:
        RuntimeError:
            If we can't get version information from the stored version then
            this function will fail. Normally though, assuming this adapter
            was built correctly, this shouldn't occur.

    Returns:
        str: The absolute path to a Nuke executable.

    '''
    major, minor, _ = get_version_parts(version)

    if not major:
        raise RuntimeError(
            'Version "{version}" has no major component. This should not happen.'
            ''.format(version=version))

    if not minor:
        raise RuntimeError(
            'Version "{version}" has no minor component. This should not happen.'
            ''.format(version=version))

    return set([
        r'C:\Program Files\Nuke{version}\Nuke{major}.{minor}.exe'.format(
            version=version,
            major=major,
            minor=minor,
        ),
    ])


def get_version_parts(text):
    '''tuple[str, str, str]: Find the major, minor, and patch data of `text`.'''
    match = VERSION_PARSER.match(text)

    if not match:
        return ('', '', '')

    return (match.group('major'), match.group('minor'), match.group('patch'))
