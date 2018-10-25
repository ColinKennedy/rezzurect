#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The Windows class which builds Houdini Rez packages for the user.'''

# IMPORT LOCAL LIBRARIES
from . import houdini_setting
from . import helper


class WindowsHoudiniSettingAdapter(houdini_setting.CommonHoudiniSettingAdapter):

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
        return helper.get_preinstalled_windows_executables(self.version)

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.'''
        super(WindowsHoudiniSettingAdapter, self).execute()
