#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Maya Rez package in Linux.'''

# IMPORT LOCAL LIBRARIES
from ..maya_installation import helper
from . import maya_setting


class LinuxMayaSettingAdapter(maya_setting.CommonMayaSettingAdapter):

    '''An adapter which is used to set up common settings / aliases for Maya.'''

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
        return helper.get_preinstalled_linux_executables(self.version)

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(LinuxMayaSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Maya versions in Linux
