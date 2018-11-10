#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A DCC-agnostic adapter class to inherit and extend for software.'''

# IMPORT STANDARD LIBRARIES
import logging
import tarfile
import abc
import os

# IMPORT LOCAL LIBRARIES
from ..strategies import internet
from ..utils import progressbar
from ..vendors import six


_LOGGER = logging.getLogger('rezzurect.base_builder')


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

    @classmethod
    def _extract_tar(cls, source, version):
        '''Extract the TAR archive to get the main folder.

        Args:
            source (str): The absolute path to this Rez package's version folder.
            version (str): The raw version information which is used to "find"
                           the TAR archive name. Example: "11.2v3".

        Raises:
            EnvironmentError: If no archive file could be found.

        '''
        path = cls.get_archive_path_from_version(source, version)

        if not os.path.isfile(path):
            raise EnvironmentError('Tar file "{path}" does not exist.'
                                   ''.format(path=path))

        cls._extract_tar_file(path)

    @staticmethod
    def _extract_tar_file(path, destination=''):
        '''Extract the given TAR archive file to some path on-disk.

        Args:
            path (str):
                The location of the TAR archive to extract.
            destination (str, optional):
                The location where `path` TAR will be extracted to.
                If no destination is given, the TAR archive's directory will
                be used instead. Default: "".

        '''
        if not destination:
            destination = os.path.dirname(path)

        _LOGGER.debug('Extracting tar file "%s".', path)

        with tarfile.open(fileobj=progressbar.TarProgressFile(path, logger=_LOGGER.trace)) as tar:
            try:
                tar.extractall(path=destination)
            except Exception:
                _LOGGER.exception('Tar file "%s" failed to extract.', path)
                raise
            else:
                _LOGGER.debug('Tar extraction finished.')

    @abc.abstractmethod
    def install_from_local(self, source, install):
        '''Search for a locally-installed package file and install it, if it exists.

        Args:
            source (str):
                The absolute path to the package folder where the executable
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        Returns:
            str: The absolute path to the executable file which is used for installation.

        '''
        return ''

    @staticmethod
    def get_archive_folder(root):
        '''str: Get the recommended folder for archive (installer) files to be.'''
        return os.path.join(root, 'archive')

    @classmethod
    def get_archive_path(cls, root, file_name):
        '''str: Get the recommended folder for archive (installer) files to be.'''
        return os.path.join(cls.get_archive_folder(root), file_name)

    @staticmethod
    @abc.abstractmethod
    def get_archive_path_from_version(source, install):
        return ''

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

        _LOGGER.debug('Finding strategy order for "%s".', cls.__name__)

        default_order = [name for name, _ in cls.strategies]

        package_order = os.getenv('REZZURECT_{name}_STRATEGY_ORDER'
                                  ''.format(name=cls.name.upper()), '')

        if package_order:
            _LOGGER.debug('Package order "%s" was found.', package_order)
            return _split(package_order)

        global_order = os.getenv('REZZURECT_STRATEGY_ORDER', '')

        if global_order:
            _LOGGER.debug('Global order "%s" was found.', global_order)
            return _split(global_order)

        _LOGGER.debug('Default order "%s" will be used.', default_order)

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
                _LOGGER.exception('Strategy "%s" did not succeed.', name)
            else:
                _LOGGER.info('Strategy "%s" succeeded.', name)
                return

        raise RuntimeError(
            'No strategy in "{obj.name}" to install the package suceeded. '
            'The strategies were, "{strategies}".'
            ''.format(obj=self, strategies=[name for name, _ in strategies]))

    @abc.abstractmethod
    def get_preinstalled_executables(self):
        '''str: Get a list of possible pre-installed executable files for this package.'''
        return set()


def add_from_internet_build(package, system, architecture, source_path, install_path, adapter):
    '''Download the installer for `package` and then install it.

    Args:
        package (str):
            The name of packaget to get an installer from online.
        system (str):
            The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str):
            The bits of the `system`. Example: "x86_64", "AMD64", etc.
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.
        adapter (`rezzurect.adapters.base_builder.BaseAdapter`):
            The object which is used to "install" the files.

    Raises:
        RuntimeError: If the download failed to install into `destination`.

    '''
    destination = adapter.get_archive_folder(source_path)

    destination = internet.download(
        package,
        adapter.version,
        system,
        architecture,
        destination,
    )

    if not os.path.isfile(destination):
        raise RuntimeError(
            'Package/Version "{package}/{adapter.version}" could not be downloaded to path, '
            '"{destination}".'.format(package=package, adapter=adapter, destination=destination))

    _LOGGER.info(
        'Downloaded package/version "%s/%s" to path, "%s".',
        package,
        adapter.version,
        destination,
    )

    add_local_filesystem_build(source_path, install_path, adapter)


def add_link_build(adapter):
    '''Add the command which lets the user link Rez to an existing install.

    Args:
        adapter (`rezzurect.adapters.base_builder.BaseAdapter`):
            The object which is used to search for existing installs.

    Raises:
        RuntimeError: If no valid executable could be found.

    '''
    paths = adapter.get_preinstalled_executables()

    for path in paths:
        if os.path.isfile(path):
            return

    raise RuntimeError('No expected binary file could be found. '
                       'Checked "{paths}".'.format(paths=', '.join(sorted(paths))))


def add_local_filesystem_build(source_path, install_path, adapter):
    '''Search the user's files and build the Rez package.

    Args:
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.
        adapter (`rezzurect.adapters.base_builder.BaseAdapter`):
            The object which is used to "install" the files.

    '''
    if not os.path.isdir(install_path):
        os.makedirs(install_path)

    adapter.install_from_local(source_path, install_path)
