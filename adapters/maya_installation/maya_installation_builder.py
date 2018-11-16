#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of general adapter classes which can be used to build Rez packages.'''

# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import logging
import zipfile
import stat
import os

# IMPORT LOCAL LIBRARIES
from .. import base_builder
from ... import chooser
from . import helper


_DEFAULT_VALUE = object()
LOGGER = logging.getLogger('rezzurect.maya_installation_builder')


class BaseMayaAdapter(base_builder.BaseAdapter):

    '''An base-class which is meant share code across subclasses.

    This class is not meant to be used directly.

    '''

    _install_archive_name_template = ''
    _install_folder_template = ''

    @classmethod
    def get_archive_path_from_version(cls, source, version):
        '''str: Get the recommended folder for archive (installer) files to be.'''
        try:
            major = helper.get_version_parts(version)
        except TypeError:
            major = version

        file_name = cls._install_archive_name_template.format(major=major)

        return cls.get_archive_path(source, file_name)

    @classmethod
    def get_install_folder(cls, root, version):
        # '''Get the absolute path to where the expected Nuke install file is.

        # Args:
        #     root (str):
        #         The absolute path to the package folder where the Nuke executable
        #         would be found.
        #     version (str):
        #         The full, unparsed version information to get an executable of.
        #         Example: "11.2v3".

        # Returns:
        #     str: The absolute path to the executable file of the given `version`.

        # '''
        major = helper.get_version_parts(version)

        return cls.get_archive_path(
            root,
            cls._install_folder_template.format(major=major),
        )

    def install_from_local(self, source, install):
        '''Search for an extracted Maya folder and install it's RPMs, if it exists.

        Args:
            source (str):
                The absolute path to the package folder where the Maya folder
                would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        Raises:
            EnvironmentError: If the folder could not be found.

        Returns:
            str: The absolute path to the folder which is used for installation.

        '''
        directory = self.get_install_folder(source, self.version)

        if not os.path.isdir(directory):
            raise EnvironmentError(
                'directory "{directory}" does not exist. '
                'Check its spelling and try again.'.format(directory=directory))

        return directory


class LinuxAdapter(BaseMayaAdapter):

    '''An adapter for installing Maya onto a Linux machine.'''

    name = 'maya'
    _install_archive_name_template = 'Autodesk_Maya_{major}_EN_Linux_64bit.tgz'
    _install_folder_template = 'Autodesk_Maya_{major}_EN_Linux_64bit'

    @classmethod
    def _extract_tar(cls, source, version):
        '''Extract the TAR archive to get Maya's main installation folder.

        Args:
            source (str): The absolute path to this Rez package's version folder.
            version (str): The raw version information which is used to "find"
                           the TAR archive name. Example: "2018".

        Raises:
            EnvironmentError: If no archive file could be found.

        '''
        path = cls.get_archive_path_from_version(source, version)

        if not os.path.isfile(path):
            raise EnvironmentError('Tar file "{path}" does not exist.'
                                   ''.format(path=path))

        root = os.path.dirname(path)
        base_name = os.path.splitext(os.path.basename(path))[0]
        destination = os.path.join(root, base_name)

        cls._extract_tar_file(path, destination)

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
        return helper.get_preinstalled_linux_executables(self.version)

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
        try:
            directory = super(LinuxAdapter, self).install_from_local(source, install)
        except EnvironmentError:
            self._extract_tar(source, self.version)
            directory = super(LinuxAdapter, self).install_from_local(source, install)

        major = helper.get_version_parts(self.version)

        main_rpm_file = os.path.join(directory, 'Maya{major}_64-2018.0-5870.x86_64.rpm'.format(major=major))

        # TODO : Replace rpm2cpio with a better method, later
        command = 'cd "{install}" && rpm2cpio "{main_rpm_file}" | cpio -idmv' \
            ''.format(install=install, main_rpm_file=main_rpm_file)
        stdout, stderr = subprocess.Popen(
            [command],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()

#         major, minor, _ = helper.get_version_parts(self.version)
#         executable = 'Nuke{major}.{minor}'.format(major=major, minor=minor)
#         executable = os.path.join(install, executable)

#         if not os.path.isfile(executable):
#             raise EnvironmentError('Zip failed to extract to folder "{install}".'
#                                    ''.format(install=install))

#         # Reference: https://stackoverflow.com/questions/12791997
#         executable_stats = os.stat(executable)
#         os.chmod(executable, executable_stats.st_mode | stat.S_IEXEC)


def register(source_path, install_path, system, architecture):
    '''Add installation options to all of the Maya adapter classes.

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

    '''
    adapters = (
        ('Linux', LinuxAdapter),
    )

    for system_, adapter in adapters:
        adapter.strategies = []

        add_maya_from_internet_build = functools.partial(
            base_builder.add_from_internet_build,
            'maya', system, architecture, source_path, install_path)
        add_maya_local_filesystem_build = functools.partial(
            base_builder.add_local_filesystem_build, source_path, install_path)

        adapter.strategies.append(('local', add_maya_local_filesystem_build))
        # TODO : Add internet strategy again
        # adapter.strategies.append(('internet', add_maya_from_internet_build))
        # adapter.strategies.append(('link', base_builder.add_link_build))

        chooser.register_build_adapter(adapter, 'maya_installation', system_)
