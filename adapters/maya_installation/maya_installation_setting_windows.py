#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Maya Rez package in Windows.'''

# IMPORT LOCAL LIBRARIES
from . import maya_installation_setting
from . import helper


class WindowsMayaSettingAdapter(maya_installation_setting.CommonMayaSettingAdapter):

    '''An adapter which is used to set up common settings / aliases for Maya.'''

    def get_executable_command(self):
        '''str: The command needed to run Maya.'''
        return 'maya.exe'

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Maya files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Maya executable.

        '''
        return helper.get_preinstalled_windows_executables(self.version)

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(WindowsMayaSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Maya versions in Windows.
