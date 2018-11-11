#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Houdini Rez package in Linux.'''

# IMPORT LOCAL LIBRARIES
from . import houdini_installation_setting
from . import helper


class LinuxHoudiniSettingAdapter(houdini_installation_setting.CommonHoudiniSettingAdapter):

    '''An adapter which is used to set up common settings / aliases for Houdini.'''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Houdini files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Houdini executable.

        '''
        return helper.get_preinstalled_linux_executables(self.version)

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(LinuxHoudiniSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Houdini versions in Linux.
