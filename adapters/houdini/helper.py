#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Any information that is used between one or more adapter modules.'''


def get_preinstalled_linux_executables(version):
    '''Get a list of possible pre-installed executable Houdini files.

    Args:
        version (str): A version of Houdini. Example: "17.0.352".

    Raises:
        RuntimeError:
            If we can't get version information from the stored version then
            this function will fail. Normally though, assuming this adapter
            was built correctly, this shouldn't occur.

    Returns:
        str: The absolute path to a Houdini executable.

    '''
    major, minor, patch = get_version_parts(version)

    if not major:
        raise RuntimeError(
            'Version "{version}" has no major component. This should not happen.'
            ''.format(version=version))

    if not minor:
        raise RuntimeError(
            'Version "{version}" has no minor component. This should not happen.'
            ''.format(version=version))

    if not patch:
        raise RuntimeError(
            'Version "{version}" has no patch component. This should not happen.'
            ''.format(version=version))

    return {'/opt/hfs{version}/bin/houdini'.format(version=version), }


def get_preinstalled_windows_executables(version):
    # '''Get a list of possible pre-installed executable Houdini files.

    # Args:
    #     version (str): A version of Houdini. Example: "17.0.352".

    # Raises:
    #     RuntimeError:
    #         If we can't get version information from the stored version then
    #         this function will fail. Normally though, assuming this adapter
    #         was built correctly, this shouldn't occur.

    # Returns:
    #     str: The absolute path to a Houdini executable.

    # '''
    raise NotImplementedError('need to write this')
    # major, minor, patch = get_version_parts(version)

    # if not major:
    #     raise RuntimeError(
    #         'Version "{version}" has no major component. This should not happen.'
    #         ''.format(version=version))

    # if not minor:
    #     raise RuntimeError(
    #         'Version "{version}" has no minor component. This should not happen.'
    #         ''.format(version=version))

    # if not patch:
    #     raise RuntimeError(
    #         'Version "{version}" has no patch component. This should not happen.'
    #         ''.format(version=version))

    # return {'/opt/hfs{version}/bin/houdini'.format(version=version), }


def get_version_parts(text):
    '''tuple[str, str, str]: Find the major, minor, and patch data of `text`.'''
    return tuple(text.split('.'))
