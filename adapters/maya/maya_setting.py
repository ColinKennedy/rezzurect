#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter (and its functions) for creating and running a Maya Rez package.'''

# IMPORT LOCAL LIBRARIES
from ..maya_installation import helper
from .. import common_setting


class CommonMayaSettingAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Maya.'''

    name = 'maya'

    def get_executable_command(self):
        '''The command needed to run Maya.

        Raises:
            EnvironmentError: If the stored version is incorrect.

        Returns:
            str: The found command for Maya's version.

        '''
        return 'maya.exe'

    def get_install_root(self):
        '''str: The absolute path to Maya's Rez package installation directory.'''
        return self.env.MAYA_INSTALL_ROOT.get()

    def execute(self):  # pylint: disable=useless-super-delegation
        super(CommonMayaSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Maya versions in all OSes.
