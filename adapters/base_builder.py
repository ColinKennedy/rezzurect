#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A DCC-agnostic adapter class to inherit and extend for software.'''

# IMPORT STANDARD LIBRARIES
import logging
import abc
import os

# IMPORT THIRD-PARTY LIBRARIES
import six


LOGGER = logging.getLogger('rezzurect.nuke_builder')


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):

    '''An adapter for installing the package onto the user's system.'''

    name = ''
    strategies = []

    def __init__(self, version, architecture):
        '''Create the instance and store the user's architecture.

        Args:
            version (str):
                The specific install of `package`.
            architecture (str):
                The bits of the `system`. Example: "x86_64", "AMD64", etc.

        '''
        super(BaseAdapter, self).__init__()
        self.version = version
        self.architecture = architecture

    @abc.abstractmethod
    def install_from_local(self, source, install):
        '''Search for a locally-installed Nuke file and install it, if it exists.

        Args:
            source (str):
                The absolute path to the package folder where the Nuke executable
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        Returns:
            str: The absolute path to the executable file which is used for installation.

        '''
        return ''

    # TODO : Consider making `definition` into a dict
    @staticmethod
    def get_archive_path(root, file_name):
        '''str: Get the recommended folder for archive (installer) files to be.'''
        return os.path.join(root, 'archive', file_name)

    @classmethod
    def get_strategy_order(cls):
        '''Find the strategy execution order for this adapter.

        If an environment variable matching this adapter's name is found,
        then that order will be used. If a global strategy order has been defined
        then that will be used instead. If neither exist, use the order that
        the strategies were registered with.

        Note:
            If a global or package environment variable is defined and this class
            has a registered strategy that is not listed in either, it is ignored
            and will not execute.

        Returns:
            list[str]:
                The names of each strategy in the order that they should be tried.

        '''
        def _split(variable):
            items = []

            for item in variable.split(','):
                item = item.strip()

                if item:
                    items.append(item)

            return items

        LOGGER.debug('Finding strategy order for "%s".', cls.__name__)

        default_order = [name for name, _ in cls.strategies]

        package_order = os.getenv('REZZURECT_{name}_STRATEGY_ORDER'
                                  ''.format(name=cls.name.upper()), '')

        if package_order:
            LOGGER.debug('Package order "%s" was found.', package_order)
            return _split(package_order)

        global_order = os.getenv('REZZURECT_STRATEGY_ORDER', '')

        if global_order:
            LOGGER.debug('Global order "%s" was found.', global_order)
            return _split(global_order)

        LOGGER.debug('Default order "%s" will be used.', default_order)

        return default_order

    @classmethod
    def get_strategies(cls):
        '''Get registered build strategies for this class in execution-order.

        Returns:
            list[str, callable[`rezzurect.adapters.base_builder.BaseAdapter`]]:
                The found strategies.

        '''
        strategies = {name: strategy for name, strategy in cls.strategies}
        order = cls.get_strategy_order()
        return [(name, strategies[name]) for name in order]

    def make_install(self):
        '''Try different build methods until something works.

        Raises:
            RuntimeError: If all found build methods fail.

        '''
        strategies = self.get_strategies()

        for name, choice in strategies:
            try:
                choice(self)
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception('Strategy "%s" did not succeed.', name)
            else:
                LOGGER.info('Strategy "%s" succeeded.', name)
                return

        raise RuntimeError(
            'No strategy to install the package suceeded. The strategies were, '
            '"{strategies}".'.format(strategies=[name for name, _ in strategies]))

    @abc.abstractmethod
    def get_preinstalled_executables(self):
        '''str: Get a list of possible pre-installed executable Nuke files.'''
        return set()
