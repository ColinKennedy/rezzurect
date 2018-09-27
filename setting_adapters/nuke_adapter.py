#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter (and its functions) for creating and running a Nuke Rez package.'''

# IMPORT STANDARD LIBRARIES
import re

# IMPORT LOCAL LIBRARIES
import common


_VERSION_PARSER = re.compile(r'(?P<major>\d+).(?P<minor>\d+)v(?P<patch>\d+)')


class NukeAdapter(common.AbstractBaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Nuke.'''

    name = 'nuke'

    def __init__(self, alias_manager, include_common_aliases=True):
        '''Create the adapter and add the session's alias class.

        Args:
            alias_manager (`rez_helper.adapters.common.BaseAdapter` or NoneType):
                The class which is used to add aliases to the OS.
            include_common_aliases (`bool`, optional):
                If True, add a "main" alias to the current session.
                If False, don't add it.
                Default is True.

        '''
        super(NukeAdapter, self).__init__(alias_manager)

    @staticmethod
    def _get_executable_command(version):
        '''str: The command that is run as the "main" alias.'''
        match = _VERSION_PARSER.match(version)

        if not match:
            raise EnvironmentError(
                'version "{version}" did not match expected pattern, '
                '"{_VERSION_PARSER.pattern}"'.format(
                    version=version,
                    _VERSION_PARSER=_VERSION_PARSER.pattern,
                )
            )

        # The Nuke command on linux is
        version = '.'.join([match.group('major'), match.group('minor')])
        return 'Nuke{version} -nc'.format(version=version)
