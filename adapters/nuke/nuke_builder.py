#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of general adapter classes which can be used to build Rez packages.'''

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
from ... import chooser
from . import helper


_DEFAULT_VALUE = object()
LOGGER = logging.getLogger('rezzurect.nuke_builder')


class BaseNukeAdapter(base_builder.BaseAdapter):

    '''An base-class which is meant share code across subclasses.

    This class is not meant to be used directly.

    Attributes:
        _install_file_name_template (str):
            The name of the actual file which can be used to install Nuke.
            The exact name should be whatever the third-party vendor prefers.
            Make sure to include any version information in the name, such as
            "Nuke{major}.{minor}v{patch}-win-x86-release-64.exe" or
            "Nuke{major}.{minor}v{patch}-linux-x86-release-64-installer".

    '''

    _install_file_name_template = ''

    def __init__(self, version, architecture):
        '''Create the instance and store the user's architecture.

        Args:
            version (str):
                The specific install of `package`.
            architecture (str):
                The bits of the `system`. Example: "x86_64", "AMD64", etc.

        '''
        super(BaseNukeAdapter, self).__init__(version, architecture)

    @staticmethod
    def _get_version_parts(text):
        '''tuple[str, str, str]: Find the major, minor, and patch data of `text`.'''
        match = helper.VERSION_PARSER.match(text)

        if not match:
            return ('', '', '')

        return (match.group('major'), match.group('minor'), match.group('patch'))

    @classmethod
    def get_install_file(cls, root, version):
        '''Get the absolute path to where the expected Nuke install file is.

        Args:
            root (str):
                The absolute path to the package folder where the Nuke executable
                would be found.
            version (str):
                The full, unparsed version information to get an executable of.
                Example: "11.2v3".

        Returns:
            str: The absolute path to the executable file of the given `version`.

        '''
        major, minor, patch = cls._get_version_parts(version)

        return cls.get_archive_path(
            root,
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

    def __init__(self, version, architecture):
        '''Create the instance and store the user's architecture.

        Args:
            version (str):
                The specific install of `package`.
            architecture (str):
                The bits of the `system`. Example: "x86_64", "AMD64", etc.

        '''
        super(LinuxAdapter, self).__init__(version, architecture)

    @classmethod
    def _extract_tar(cls, source, version):
        '''Extract the Nuke TAR archive to get the Nuke ZIP installer.

        Args:
            source (str): The absolute path to this Rez package's version folder.
            version (str): The raw version information which is used to "find"
                           the TAR archive name. Example: "11.2v3".

        Raises:
            EnvironmentError: If no archive file could be found.

        '''
        (major, minor, patch) = version

        file_name = 'Nuke{major}.{minor}v{patch}-linux-x86-release-64.tgz'.format(
            major=major, minor=minor, patch=patch,
        )

        path = cls.get_archive_path(source, file_name)

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

        Raises:
            EnvironmentError: If the Zip file failed to extract Nuke into `install`.

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
        '''Get a list of possible pre-installed executable Nuke files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Nuke executable.

        '''
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

    def __init__(self, version, architecture):
        '''Create the instance and store the user's architecture.

        Args:
            version (str):
                The specific install of `package`.
            architecture (str):
                The bits of the `system`. Example: "x86_64", "AMD64", etc.

        '''
        super(WindowsAdapter, self).__init__(version, architecture)

    @staticmethod
    def _get_base_command(executable, root):
        '''Make the command used to install Nuke, on Windows.

        Args:
            executable (str): The absolute path to the ".exe" installer file to run.
            root (str): The absolute directory to where the ".exe" will send files to.

        '''
        # Reference: https://learn.foundry.com/nuke/content/getting_started/installation/installing_nuke_win.html
        #
        # Note: The ".exe" file normally gives you a few window prompts to have
        #       to click through.  We add "/silent" to skip these prompts and
        #       go straight to installation. Use "/verysilent" to hide the
        #       install progress bar.
        #
        return '{executable} /dir="{root}" /silent'.format(
            executable=executable, root=root)

    def install_from_local(self, source, install):
        '''Search for a local Nuke install-executable and run it, if it exists.

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
        '''Get a list of possible pre-installed executable Nuke files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Nuke executable.

        '''
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
    '''Search the user's files and build the Rez package.

    Args:
        adapter (`rezzurect.adapters.base_builder.BaseAdapter`):
            The object which is used to "install" the files.
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.

    '''
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
    raise NotImplementedError("Need to write this")


def register(source_path, install_path, system, distribution, architecture):
    '''Add installation options to all of the Nuke adapter classes.

    Each of the installation options take only one arg, which is the adapter
    which is used to handle the request. If the request is successful then the
    function should just complete. If it fails for whatever reason then
    have the function raise any exception.

    Args:
        source_path (str):
            The absolute path to where the Rez package is located, on-disk.
        install_path (str):
            The absolute path to where the package will be installed into.
        system (str):
            The name of the OS platform. Example: "Linux", "Windows", etc.
        architecture (str):
            The bits of the `system`. Example: "x86_64", "AMD64", etc.
        distribution (str):
            The name of the type of OS (Example: "CentOS", "windows", etc.)

    '''
    adapters = (
        ('Linux', LinuxAdapter),
        ('Windows', WindowsAdapter),
    )

    for system_, adapter in adapters:
        adapter.strategies = []

        add_nuke_from_internet_build = functools.partial(
            add_from_internet_build,
            internet.download, 'nuke', system, distribution, architecture)
        add_nuke_local_filesystem_build = functools.partial(
            add_local_filesystem_build, source_path, install_path)

        adapter.strategies.append(('local', add_nuke_local_filesystem_build))
        adapter.strategies.append(('link', add_link_build))
        adapter.strategies.append(('internet', add_nuke_from_internet_build))

        chooser.register_build_adapter(adapter, 'nuke_installation', system_)
