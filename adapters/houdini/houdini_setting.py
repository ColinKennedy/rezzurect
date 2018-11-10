#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Houdini Rez package.'''

# IMPORT LOCAL LIBRARIES
from .. import common_setting


class CommonHoudiniSettingAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Houdini.'''

    name = 'houdini'

    @staticmethod
    def get_executable_command():
        '''The command needed to run Houdini.

        Returns:
            str: The found command for Houdini's version.

        '''
        return 'houdini-bin'

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(CommonHoudiniSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Houdini versions in all OSes.
