#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Maya Rez package.'''

# IMPORT LOCAL LIBRARIES
from .. import common_setting
from . import helper


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
        match = helper.VERSION_PARSER.match(self.version)

        if not match:
            raise EnvironmentError(
                'version "{obj.version}" did not match expected pattern, '
                '"{parser.pattern}"'.format(
                    obj=self.version,
                    parser=helper.VERSION_PARSER,
                )
            )

        return 'maya{version}'.format(version=match.group('major'))

    def execute(self):  # pylint: disable=useless-super-delegation
        '''Add aliases and environment variables to the package on-startup.'''
        super(CommonMayaSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Maya versions in all OSes.
