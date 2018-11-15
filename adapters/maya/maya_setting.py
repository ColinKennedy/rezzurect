#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter (and its functions) for creating and running a Nuke Rez package.'''

# IMPORT LOCAL LIBRARIES
from ..nuke_installation import helper
from .. import common_setting


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

    def execute(self):  # pylint: disable=useless-super-delegation
        super(CommonNukeSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Nuke versions in all OSes.
