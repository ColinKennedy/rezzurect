#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import getpass
import logging
import abc
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez.vendor.version import version as version_
from rez import package_maker__ as package_maker
from rez import config
import six

# IMPORT LOCAL LIBRARIES
from .. import manager


LOGGER = logging.getLogger('rezzurect.nuke_builder')


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):

    '''An adapter for installing the package onto the user's system.'''

    name = ''
    strategies = []

    def __init__(self, version, system, architecture):
        # '''Create the instance and store the user's architecture.

        # Args:
        #     architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

        # '''
        super(BaseAdapter, self).__init__()
        self.version = version
        self.system = system
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

        Raises:
            EnvironmentError: If the executable file could not be found.

        Returns:
            str: The absolute path to the executable file which is used for installation.

        '''
        return ''

    # TODO : Consider making `definition` into a dict
    @staticmethod
    def make_package(definition, root=''):
        if not root:
            root = config.config.get('local_packages_path')

        if not os.path.isdir(root):
            os.makedirs(root)

        with package_maker.make_package(definition.name, root) as pkg:
            manager.mirror('authors', definition, pkg, default=[getpass.getuser()])
            manager.mirror('commands', definition, pkg)
            manager.mirror('description', definition, pkg)
            manager.mirror('help', definition, pkg, default='')
            manager.mirror('name', definition, pkg)
            manager.mirror('timestamp', definition, pkg)
            manager.mirror('tools', definition, pkg)
            # mirror('uuid', definition, pkg, default=str(uuid.uuid4()))
            pkg.version = version_.Version(definition.version)

    @classmethod
    def get_strategy_order(cls):
        def _split(variable):
            items = []
            for item in variable.split(','):
                item = item.strip()

                if item:
                    items.append(item)

            return item

        LOGGER.debug('Finding strategy order for "{obj.__name__}".'
                     ''.format(obj=cls))

        default_order = [name for name, _ in cls.strategies]

        global_order = os.getenv('REZZURECT_STRATEGY_ORDER', '')

        if global_order:
            LOGGER.debug('Global order "{global_order}" was found.'.format(
                global_order=global_order))
            return _split(global_order)

        package_order = os.getenv('REZZURECT_{name}_STRATEGY_ORDER'
                                  ''.format(name=cls.name.upper()), '')

        if package_order:
            LOGGER.debug('Package order "{package_order}" was found.'.format(
                package_order=package_order))
            return _split(package_order)

        LOGGER.debug('Default order "{default_order}" will be used.'.format(
            default_order=default_order))

        return default_order

    @classmethod
    def get_strategies(cls):
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
                LOGGER.exception('strategy "{name}" did not succeed.'.format(name=name))
            else:
                LOGGER.info('strategy "{name}" succeeded.'.format(name=name))
                return

        raise RuntimeError(
            'No strategy to install the package suceeded. The strategies were, '
            '"{strategies}".'.format(strategies=[name for name, _ in strategies]))

    @abc.abstractmethod
    def get_preinstalled_executables(self):
        return set()
