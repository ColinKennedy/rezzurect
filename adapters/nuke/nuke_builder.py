#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''General adapter classes which can be used to build Rez packages.'''

# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import itertools
import getpass
import logging
import tarfile
import zipfile
import ftplib
import stat
import abc
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez.vendor.version import version as version_
from rez import package_maker__ as package_maker
from rez import config

# IMPORT LOCAL LIBRARIES
from ...strategies import internet
from ...utils import progressbar
from ...vendors import six
from ... import chooser
from ... import manager
from . import helper


_DEFAULT_VALUE = object()
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

    @staticmethod
    def _get_version_parts(text):
        match = helper.VERSION_PARSER.match(text)

        if not match:
            return ('', '', '')

        return (match.group('major'), match.group('minor'), match.group('patch'))

    @classmethod
    def get_install_file(cls, root, version):
        '''str: Get the absolute path to where the expected Nuke install file is.'''
        major, minor, patch = cls._get_version_parts(version)

        return os.path.join(
            root,
            'archive',
            cls._install_file_name_template.format(major=major, minor=minor, patch=patch),
        )

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
        executable = self.get_install_file(source, self.version)

        if not os.path.isfile(executable):
            raise EnvironmentError(
                'install_file "{executable}" does not exist. '
                'Check its spelling and try again.'.format(executable=executable))

        return executable

    @classmethod
    def install_from_ftp(cls, server, source, install):
        ftp = ftplib.FTP()

        # TODO : Default host / port?
        host = os.environ['REZZURECT_FTP_HOST']
        port = os.environ['REZZURECT_FTP_PORT']
        user = os.environ['REZZURECT_FTP_USER']
        password = os.environ['REZZURECT_FTP_PASSWORD']
        ftp.connect(host, port)
        ftp.login(user, password)

        # TODO : Make this work
        # TODO : Make progress-bar
        #        https://stackoverflow.com/questions/11623964/python-ftp-and-progressbar-2-3

        destination = '/tmp/somewhere'
        ftp.retrbinary(
            'RETR {filename}'.format(filename='FOO FILENAME'))

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


class LinuxAdapter(BaseAdapter):

    '''An adapter for installing Nuke onto a Linux machine.'''

    name = 'nuke'
    _install_file_name_template = 'Nuke{major}.{minor}v{patch}-linux-x86-release-64-installer'

    def __init__(self, version, system, architecture):
        # '''Create the instance and store the user's architecture.

        # Args:
        #     architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

        # '''
        super(LinuxAdapter, self).__init__(version, system, architecture)

    @staticmethod
    def _extract_tar(source, version):
        (major, minor, patch) = version

        file_name = 'Nuke{major}.{minor}v{patch}-linux-x86-release-64.tgz'.format(
            major=major, minor=minor, patch=patch,
        )

        path = os.path.join(source, 'archive', file_name)

        if not os.path.isfile(path):
            raise EnvironmentError('Tar file "{path}" does not exist.'
                                   ''.format(path=path))

        LOGGER.debug('Extracting tar file "{path}".'.format(path=path))

        with tarfile.open(fileobj=progressbar.ProgressFileObject(path, logger=LOGGER.trace)) as tar:
            try:
                tar.extractall(path=os.path.dirname(path))
            except Exception:
                LOGGER.exception('Tar file "{path}" failed to extract.'.format(path=path))
                raise

    def install_from_local(self, source, install):
        '''Unzip the Nuke file to the given install folder.

        Args:
            source (str):
                The absolute path to the package folder where the Nuke executable
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        '''
        major, minor, patch = self._get_version_parts(self.version)

        try:
            zip_file_path = super(LinuxAdapter, self).install_from_local(source, install)
        except EnvironmentError:
            self._extract_tar(source, (major, minor, patch))
            zip_file_path = super(LinuxAdapter, self).install_from_local(source, install)

        LOGGER.debug('Unzipping "{zip_file_path}".'.format(zip_file_path=zip_file_path))

        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            try:
                zip_file.extractall(install)
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception('Zip file "{zip_file_path}" failed to unzip.'.format(zip_file_path=zip_file_path))
                raise

        executable = 'Nuke{major}.{minor}'.format(major=major, minor=minor)
        executable = os.path.join(install, executable)

        if not os.path.isfile(executable):
            raise EnvironmentError('Zip failed to extract to folder "{install}".'
                                   ''.format(install=install))

        # Reference: https://stackoverflow.com/questions/12791997
        st = os.stat(executable)
        os.chmod(executable, st.st_mode | stat.S_IEXEC)

    def get_preinstalled_executables(self):
        major, minor = self._get_version_parts(self.version)

        if not major:
            raise RuntimeError(
                'Version "{obj.version}" has no major component. This should not happen.'
                ''.format(obj=self))

        if not minor:
            raise RuntimeError(
                'Version "{obj.version}" has no minor component. This should not happen.'
                ''.format(obj=self))

        options = [
            '/usr/local/Nuke{obj.version}/Nuke{major}.{minor}',
            os.path.expanduser('~/Nuke{obj.version}/Nuke{major}.{minor}'),
        ]

        return set((path.format(obj=self, major=major, minor=minor)
                    for path in options))


class WindowsAdapter(BaseAdapter):

    '''An adapter for installing Nuke onto a Windows machine.'''

    name = 'nuke'
    _install_file_name_template = 'Nuke{major}.{minor}v{patch}-win-x86-release-64.exe'

    def __init__(self, version, system, architecture):
        # '''Create the instance and store the user's architecture.

        # Args:
        #     architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

        # '''
        super(WindowsAdapter, self).__init__(version, system, architecture)

    @staticmethod
    def _get_base_command(executable, root):
        '''str: The command used to install Nuke, on Windows.'''
        return '{executable} /dir="{root}" /silent'.format(
            executable=executable, root=root)

    def install_from_local(self, source, install):
        '''Search for a locally-installed Nuke file and install it, if it exists.

        Args:
            source (str):
                The absolute path to the package folder where the Nuke executable
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        Raises:
            RuntimeError: If the installation failed for some reason.

        '''
        executable = super(WindowsAdapter, self).install_from_local(source, install)
        command = self._get_base_command(executable, install)

        _, stderr = subprocess.Popen(
            command, stderr=subprocess.PIPE, shell=True).communicate()

        if stderr:
            raise RuntimeError('The local install failed with this message "{stderr}".'
                               ''.format(stderr=stderr))

    def get_preinstalled_executables(self):
        major, minor, _ = self._get_version_parts(self.version)

        if not major:
            raise RuntimeError(
                'Version "{obj.version}" has no major component. This should not happen.'
                ''.format(obj=self))

        if not minor:
            raise RuntimeError(
                'Version "{obj.version}" has no minor component. This should not happen.'
                ''.format(obj=self))

        return set([
            r'C:\Program Files\Nuke{obj.version}\Nuke{major}.{minor}.exe'.format(
                obj=self,
                major=major,
                minor=minor,
            ),
        ])


def add_local_filesystem_build(source_path, install_path, adapter):
    # '''Search the user's files and build the Rez package.

    # Args:
    #     adapter (`rezzurect.adapters.common.BaseAdapter`):
    #         The object which is used to "install" the files.
    #     source_path (str):
    #         The absolute path to where the Rez package is located, on-disk.
    #     install_path (str):
    #         The absolute path to where the package will be installed into.

    # '''
    if not os.path.isdir(install_path):
        os.makedirs(install_path)

    adapter.install_from_local(source_path, install_path)


def add_link_build(adapter):
    '''Add the command which lets the user link Rez to an existing install.

    Args:
        adapter (`rezzurect.adapters.common.BaseAdapter`):
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


# def add_ftp_filesystem_build(adapter, source_path, install_path):
#     '''Download the files from FTP and the Rez package if needed.

#     Args:
#         adapter (`rezzurect.adapters.common.BaseAdapter`):
#             The object which is used to "install" the files from FTP.
#         source_path (str):
#             The absolute path to where the Rez package is located, on-disk.
#         install_path (str):
#             The absolute path to where the package will be installed into.

#     '''
    # if not os.path.isdir(install_path):
    #     os.makedirs(install_path)

    # server = os.environ['REZZURECT_FTP_SERVER']

    # adapter.install_from_ftp(server, source_path, install_path)


def add_from_internet_build(package, system, distribution, architecture, adapter):
    internet.download(package, system, distribution, architecture)


def register(source_path, install_path, system, distribution, architecture):
    adapters = (
        ('Linux', LinuxAdapter),
        ('Windows', WindowsAdapter),
    )

    for system, adapter in adapters:
        adapter.strategies = []

        add_nuke_from_internet_build = functools.partial(
            add_from_internet_build,
            internet.download, 'nuke', system, distribution, architecture)
        add_nuke_local_filesystem_build = functools.partial(
            add_local_filesystem_build, source_path, install_path)

        adapter.strategies.append(('local', add_nuke_local_filesystem_build))
        adapter.strategies.append(('link', add_link_build))
        adapter.strategies.append(('internet', add_nuke_from_internet_build))

        chooser.register_platform_adapter(adapter, 'nuke_installation', system)
