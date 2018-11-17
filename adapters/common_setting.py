#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO : Renamed to "base_setting.py"
'''A set of adapters to bootstrap Rez packages.'''

# IMPORT STANDARD LIBRARIES
import abc

# IMPORT THIRD-PARTY LIBRARIES
from ..vendors import six


@six.add_metaclass(abc.ABCMeta)
class AbstractBaseAdapter(object):

    '''A basic class that creates system aliases for Rez packages.'''

    name = ''

    def __init__(self, version, env=None, alias=None):
        '''Create the adapter and add the session's alias class.

        Args:
            version (str):
                The type of the `package` to get aliases of.
            env (`rez.utils.data_utils.AttrDictWrapper`, optional):
                A class which is used to append to the user's environment variables.
            alias (callable[str, str], optional):
                A handle to the aliases which is created when a package is installed.
                This handle is used to add aliases to the final package.

        '''
        super(AbstractBaseAdapter, self).__init__()
        self.alias = alias
        self.env = env
        self.version = version

    def __make_common_aliases(self, command):
        '''Create an alias which can be used to "run" the package.'''
        self.alias('main', command)

    @staticmethod
    @abc.abstractmethod
    def get_executable_command():
        '''str: The command needed to run the program.'''
        return ''

    @staticmethod
    @abc.abstractmethod
    def get_install_root():
        '''str: Find the absolute directory to the package's main install folder.'''
        return ''

    def execute(self):
        '''Add aliases and anything else that all packages should include.'''
        command = self.get_executable_command()

        if not command:
            return

        self.__make_common_aliases(command)


class BaseAdapter(AbstractBaseAdapter):  # pylint: disable=abstract-method

    '''An adapter that implements a DCC-specific command for the user to run.'''

    name = ''

    def execute(self):
        '''Add aliases and anything else that all packages should include.'''
        super(BaseAdapter, self).execute()

        if self.name:
            self.alias(self.name, self.get_executable_command())
