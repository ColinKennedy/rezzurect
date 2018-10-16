#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Any information that is used between one or more adapter modules.'''

# IMPORT STANDARD LIBRARIES
import os
import re


VERSION_PARSER = re.compile(r'(?P<major>\d+).(?P<minor>\d+)v(?P<patch>\d+)')


# TODO : Possibly make into just a simple function
class LinuxAdapterMixin(object):

    '''A Linux-specific class which finds executable Nuke files.'''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Nuke files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Nuke executable.

        '''
        major, minor, _ = get_version_parts(self.version)

        if not major:
            raise RuntimeError(
                'Version "{obj.version}" has no major component. This should not happen.'
                ''.format(obj=self))

        if not minor:
            raise RuntimeError(
                'Version "{obj.version}" has no minor component. This should not happen.'
                ''.format(obj=self))

        options = [
            '/usr/local/Nuke{obj.version}/Nuke{major}.{minor}',
            os.path.expanduser('~/Nuke{obj.version}/Nuke{major}.{minor}'),
        ]

        return set((path.format(obj=self, major=major, minor=minor)
                    for path in options))


class WindowsAdapterMixin(object):

    '''A Windows-specific class which finds executable Nuke files.'''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Nuke files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Nuke executable.

        '''
        major, minor, _ = get_version_parts(self.version)

        if not major:
            raise RuntimeError(
                'Version "{obj.version}" has no major component. This should not happen.'
                ''.format(obj=self))

        if not minor:
            raise RuntimeError(
                'Version "{obj.version}" has no minor component. This should not happen.'
                ''.format(obj=self))

        return set([
            r'C:\Program Files\Nuke{obj.version}\Nuke{major}.{minor}.exe'.format(
                obj=self,
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
