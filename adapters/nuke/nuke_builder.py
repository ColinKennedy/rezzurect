#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''General adapter classes which can be used to build Rez packages.'''

# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import logging
import tarfile
import zipfile
import stat
import os

# IMPORT LOCAL LIBRARIES
from ...strategies import internet
from ...utils import progressbar
from .. import base_builder
from ...vendors import six
from ... import chooser
from ... import manager
from . import helper


_DEFAULT_VALUE = object()
LOGGER = logging.getLogger('rezzurect.nuke_builder')


class BaseNukeAdapter(base_builder.BaseAdapter):
    def __init__(self, version, system, architecture):
        # '''Create the instance and store the user's architecture.

        # Args:
        #     architecture (str): The bits of the `system`. Example: "x86_64", "AMD64", etc.

        # '''
        super(BaseNukeAdapter, self).__init__(version, system, architecture)

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


class LinuxAdapter(BaseNukeAdapter):

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


class WindowsAdapter(BaseNukeAdapter):

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
    #     adapter (`rezzurect.adapters.base_builder.BaseAdapter`):
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

        chooser.register_build_adapter(adapter, 'nuke_installation', system)
