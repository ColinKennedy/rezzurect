#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter (and its functions) for creating and running a Nuke Rez package.'''

# IMPORT LOCAL LIBRARIES
from .. import common_setting
from . import helper


class _CommonAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Nuke.'''

    name = 'nuke'

    def __init__(self, version, alias):
        '''Create the adapter and add the session's alias class.

        Args:
            alias_manager (`rezzurect.adapters.common.BaseAdapter` or NoneType):
                The class which is used to add aliases to the OS.
            include_common_aliases (`bool`, optional):
                If True, add a "main" alias to the current session.
                If False, don't add it.
                Default is True.

        '''
        super(_CommonAdapter, self).__init__(version, alias)

    def get_executable_command(self):
        '''str: The command that is run as the "main" alias.'''
        match = helper.VERSION_PARSER.match(self.version)

        if not match:
            raise EnvironmentError(
                'version "{obj.version}" did not match expected pattern, '
                '"{parser.pattern}"'.format(
                    obj=self.version,
                    parser=helper.VERSION_PARSER,
                )
            )

        # The Nuke command on linux is "Nuke11.2". Non-commercial is "Nuke11.2 -nc"
        version = '.'.join([match.group('major'), match.group('minor')])
        return 'Nuke{version} -nc'.format(version=version)


class LinuxNukeAdapter(_CommonAdapter):

    '''An adapter which is used to set up common settings / aliases for Nuke.'''

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
        return helper.get_preinstalled_linux_executables(self.version)


class WindowsNukeAdapter(_CommonAdapter):

    '''An adapter which is used to set up common settings / aliases for Nuke.'''

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
        return helper.get_preinstalled_windows_executables(self.version)
