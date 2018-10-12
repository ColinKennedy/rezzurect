#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''General adapter classes which can be used to build Rez packages.'''

# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import getpass
import logging
import tarfile
import zipfile
import ftplib
import stat
import abc
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez import package_maker__ as package_maker
from rez.vendor.version import version
from rez import config

# IMPORT LOCAL LIBRARIES
from ...strategies import strategy
from ...utils import progressbar
from ...vendors import six
from ... import manager
from ... import logger
from . import helper


# TODO : Generally speaking, in this document, all "11.2v3" hardcoded stuff needs to be REMOVED

LOGGER = logger.get_logger('nuke')
LOGGER.info('got logger')
_DEFAULT_VALUE = object()


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):

    '''An adapter for installing the package onto the user's system.'''

    platform = ''

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
    def _get_major_minor_version(text):
        match = helper.VERSION_PARSER.match(text)

        if not match:
            return ('', '')

        return (match.group('major'), match.group('minor'))

    @staticmethod
    @abc.abstractmethod
    def get_install_file(root):
        '''str: Get the absolute path to where the expected Nuke install file is.'''
        return ''

    @classmethod
    @abc.abstractmethod
    def install_from_local(cls, source, install):
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
        executable = cls.get_install_file(source)

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
            pkg.version = version.Version(definition.version)

    # TODO : Consider making `definition` into a dict
    @staticmethod
    def make_install():
        '''Try different build methods until something works.

        Raises:
            RuntimeError: If all found build methods fail.

        '''
        # TODO : Replace with logging messages
        # TODO : Also add a way for the adapter to say which strategies it supports
        #        BUT overridable with an environment variable!
        #
        strategies = strategy.get_strategies()

        errors = []

        for name, choice in strategies:
            try:
                choice()
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


class PassThroughAdapter(BaseAdapter):
    def get_install_file(root):
        return ''

    def install_from_local(cls, source, install):
        return ''

    def get_preinstalled_executables(self):
        return set()


class LinuxAdapter(BaseAdapter):

    '''An adapter for installing Nuke onto a Linux machine.'''

    platform = 'Linux'

    def __init__(self, version, system, architecture):
        # '''Create the instance and store the user's architecture.

        # Args:
        #     architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

        # '''
        super(LinuxAdapter, self).__init__(version, system, architecture)

    def install_from_local(cls, source, install):
        '''Unzip the Nuke file to the given install folder.

        Args:
            source (str):
                The absolute path to the package folder where the Nuke executable
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        '''
        try:
            zip_file_path = super(LinuxAdapter, cls).install_from_local(source, install)
        except EnvironmentError:
            # TODO : This path needs to be a method or something
            tar_path = os.path.join(
                source, 'archive', 'Nuke11.2v3-linux-x86-release-64.tgz')

            if not os.path.isfile(tar_path):
                raise EnvironmentError('Tar file "{tar_path}" does not exist.'
                                       ''.format(tar_path=tar_path))

            LOGGER.debug('Extracting tar file "{tar_path}".'.format(tar_path=tar_path))

            with tarfile.open(fileobj=progressbar.ProgressFileObject(tar_path, logger=LOGGER.trace)) as tar:
                try:
                    tar.extractall(path=os.path.dirname(tar_path))
                except Exception:
                    LOGGER.exception('Tar file "{tar_path}" failed to extract.'.format(tar_path=tar_path))
                    raise

            zip_file_path = super(LinuxAdapter, cls).install_from_local(source, install)

        LOGGER.debug('Unzipping "{zip_file_path}".'.format(zip_file_path=zip_file_path))

        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            try:
                zip_file.extractall(install)
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception('Zip file "{zip_file_path}" failed to unzip.'.format(zip_file_path=zip_file_path))
                raise

        executable = os.path.join(install, 'Nuke11.2')

        if not os.path.isfile(executable):
            raise EnvironmentError('Zip failed to extract to folder "{install}".'
                                   ''.format(install=install))

        # Reference: https://stackoverflow.com/questions/12791997
        st = os.stat(executable)
        os.chmod(executable, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def get_install_file(root):
        '''str: Get the absolute path to where the expected Nuke install file is.'''
        return os.path.join(root, 'archive', 'Nuke11.2v3-linux-x86-release-64-installer')

    def get_preinstalled_executables(self):
        major, minor = self._get_major_minor_version(self.version)

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

    platform = 'Windows'

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

    @staticmethod
    def get_install_file(root):
        '''str: Get the absolute path to where the expected Nuke install file is.'''
        return os.path.join(root, 'archive', 'Nuke11.2v3-win-x86-release-64.exe')

    @classmethod
    def install_from_local(cls, source, install):
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
        executable = super(WindowsAdapter, cls).install_from_local(source, install)
        command = cls._get_base_command(executable, install)

        _, stderr = subprocess.Popen(
            command, stderr=subprocess.PIPE, shell=True).communicate()

        if stderr:
            raise RuntimeError('The local install failed with this message "{stderr}".'
                               ''.format(stderr=stderr))

    def get_preinstalled_executables(self):
        major, minor = self._get_major_minor_version(self.version)

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
