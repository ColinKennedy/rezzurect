#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Houdini Rez package.'''

# IMPORT LOCAL LIBRARIES
from .. import common_setting
from . import helper


class CommonHoudiniSettingAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Houdini.'''

    name = 'houdini'

    @staticmethod
    def get_executable_command():
        '''Get the command that is run as the "main" alias.

        Raises:
            EnvironmentError: If the stored version is incorrect.

        Returns:
            str: The found command for Houdini's version.

        '''
        return 'houdini-bin'

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.'''
        super(CommonHoudiniSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Houdini versions in all OSes.
