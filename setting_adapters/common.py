#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of adapters to bootstrap Rez packages.'''

# IMPORT STANDARD LIBRARIES
import abc

# IMPORT THIRD-PARTY LIBRARIES
import six


class BaseAdapter(object):

    '''A basic class that creates system aliases for Rez packages.'''

    name = ''

    def __init__(self, alias_manager, include_common_aliases=True):
        '''Create the adapter and add the session's alias class.

        Args:
            alias_manager (`rezzurect.adapters.common.BaseAdapter` or NoneType):
                The class which is used to add aliases to the OS.
            include_common_aliases (`bool`, optional):
                If True, add a "main" alias to the current session.
                If False, don't add it.
                Default is True.

        '''
        super(BaseAdapter, self).__init__()
        self.alias_manager = alias_manager

    def __make_common_aliases(self, command):
        '''Create an alias which can be used to "run" the package.'''
        self.alias_manager('main', command)

    @staticmethod
    def _get_executable_command(version):
        '''str: The command that is run as the "main" alias, if it is enabled.'''
        return ''

    def execute(self, version):
        '''Add aliases and anything else that all packages should include.'''
        command = self._get_executable_command(version)

        if not command:
            return

        self.__make_common_aliases(command)


@six.add_metaclass(abc.ABCMeta)
class AbstractBaseAdapter(BaseAdapter):

    '''An adapter that implements a DCC-specific command for the user to run.'''

    name = ''

    @staticmethod
    @abc.abstractmethod
    def _get_executable_command(version):
        '''str: The command that is run as the "main" alias, if it is enabled.'''
        return ''

    def execute(self, version):
        '''Add aliases and anything else that all packages should include.'''
        super(AbstractBaseAdapter, self).execute(version)

        if self.name:
            self.alias_manager(self.name, self._get_executable_command(version))
