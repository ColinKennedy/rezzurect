#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT LOCAL LIBRARIES
from . import nuke_setting


class WindowsNukeSettingAdapter(nuke_setting.CommonNukeSettingAdapter):

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
