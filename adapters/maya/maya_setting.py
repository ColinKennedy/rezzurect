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
        match = helper.VERSION_PARSER.match(self.version)

        if not match:
            raise EnvironmentError(
                'version "{obj.version}" did not match expected pattern, '
                '"{parser.pattern}"'.format(
                    obj=self.version,
                    parser=helper.VERSION_PARSER,
                )
            )

        version = match.group('major')
        return 'maya{version}'.format(version=version)

    def execute(self):  # pylint: disable=useless-super-delegation
        super(CommonMayaSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Maya versions in all OSes.
