#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of adapters to bootstrap Rez packages.'''

# IMPORT STANDARD LIBRARIES
import abc

# IMPORT THIRD-PARTY LIBRARIES
from ..vendors import six


class BaseAdapter(object):

    '''A basic class that creates system aliases for Rez packages.'''

    name = ''

    def __init__(self, version, alias=None):
        # '''Create the adapter and add the session's alias class.

        # Args:
        #     alias (`rezzurect.adapters.common.BaseAdapter` or NoneType):
        #         The class which is used to add aliases to the OS.

        # '''
        super(BaseAdapter, self).__init__()
        self.alias = alias
        self.version = version

    def __make_common_aliases(self, command):
        '''Create an alias which can be used to "run" the package.'''
        self.alias('main', command)

    def get_executable_command(self):
        '''str: The command that is run as the "main" alias, if it is enabled.'''
        return ''

    def execute(self):
        '''Add aliases and anything else that all packages should include.'''
        command = self.get_executable_command()

        if not command:
            return

        self.__make_common_aliases(command)


@six.add_metaclass(abc.ABCMeta)
class AbstractBaseAdapter(BaseAdapter):

    '''An adapter that implements a DCC-specific command for the user to run.'''

    name = ''

    @abc.abstractmethod
    def get_executable_command():
        '''str: The command that is run as the "main" alias, if it is enabled.'''
        return ''

    def execute(self):
        '''Add aliases and anything else that all packages should include.'''
        super(AbstractBaseAdapter, self).execute(version)

        if self.name:
            self.alias(self.name, self.get_executable_command())
