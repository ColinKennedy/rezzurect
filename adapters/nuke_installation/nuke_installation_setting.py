#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Nuke Rez package.'''

# IMPORT LOCAL LIBRARIES
from .. import common_setting
from . import helper


class CommonNukeSettingAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Nuke.'''

    name = 'nuke'

    def get_executable_command(self):
        '''The command needed to run Nuke.

        Raises:
            EnvironmentError: If the stored version is incorrect.

        Returns:
            str: The found command for Nuke's version.

        '''
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

    def get_install_root(self):
        '''str: The absolute path to Nuke's Rez package installation directory.'''
        return self.env.NUKE_INSTALL_ROOT.get()

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(CommonNukeSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Nuke versions in all OSes.
