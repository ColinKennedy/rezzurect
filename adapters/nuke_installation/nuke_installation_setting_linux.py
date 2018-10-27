#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Nuke Rez package in Linux.'''

# IMPORT LOCAL LIBRARIES
from . import nuke_installation_setting
from . import helper


class LinuxNukeSettingAdapter(nuke_installation_setting.CommonNukeSettingAdapter):

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

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.'''
        super(LinuxNukeSettingAdapter, self).execute()
