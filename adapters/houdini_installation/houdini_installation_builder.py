#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A set of general adapter classes which can be used to build Rez packages.

Houdini-For-Linux comes with a .tar.gz file.
This file expands into a directory which contains several other .tar.gz files
as well as a "houdini.install" file. Normally, you'd want to use
"houdini.install" to build Houdini but since that installer doesn't allow you
to set a custom directory, we extract the inner .tar.gz files, ourselves, instead.

'''

# IMPORT STANDARD LIBRARIES
import functools
import logging
import glob
import os

# IMPORT LOCAL LIBRARIES
from .. import base_builder
from ... import chooser
from . import helper


_LOGGER = logging.getLogger('rezzurect.houdini_builder')


class BaseHoudiniAdapter(base_builder.BaseAdapter):

    '''An base-class which is meant share code across subclasses.

    This class is not meant to be used directly.

    '''

    # TODO : Make a note about how the tar.gz extracts a folder with the same name
    _install_archive_folder_template = 'houdini-{version}-linux_x86_64_gcc[0-9].[0-9]'
    _install_archive_name_template = 'houdini-{version}-linux_x86_64_gcc[0-9].[0-9].tar.gz'

    @classmethod
    def get_extracted_folder(cls, source, version):
        '''Find the folder that first extracted .tar.gz will make.

        Args:
            source (str):
                The absolute path to the package folder where the Houdini executable
                would be found.
            version (str):
                The specific installation of Houdini to get the folder of.
                Example: "17.0.352".

        '''
        folder_name = cls._install_archive_folder_template.format(version=version)

        try:
            return list(glob.glob(cls.get_archive_path(source, folder_name)))[0]
        except IndexError:
            return ''

    @classmethod
    def get_archive_path_from_version(cls, source, version):
        '''Get the recommended folder for archive (installer) files to be.

        Args:
            source (str):
                The absolute path to the package folder where the Houdini executable
                would be found.
            version (str):
                The specific installation of Houdini to get the folder of.
                Example: "17.0.352".

        '''
        file_name = cls._install_archive_name_template.format(version=version)

        try:
            return list(glob.glob(cls.get_archive_path(source, file_name)))[0]
        except IndexError:
            return ''


class LinuxAdapter(BaseHoudiniAdapter):

    '''An adapter for installing Houdini onto a Linux machine.'''

    name = 'houdini'

    @staticmethod
    def _get_python_tar_files(root):
        '''list[str]: Find every Python TAR archive that must be installed.'''
        root = os.path.join(root, 'python*.tar.gz')

        try:
            return list(glob.glob(root))
        except IndexError:
            return ''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Houdini files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Houdini executable.

        '''
        return helper.get_preinstalled_linux_executables(self.version)

    def install_from_local(self, source, install):
        '''Extract the TAR files for Houdini to the given install folder.

        Args:
            source (str):
                The absolute path to the package folder where the Houdini
                executable would be found.
            install (str):
                The absolute directory where `source` will be installed into.

        Raises:
            EnvironmentError: If the TAR file failed to extract into `install`.

        '''
        extracted_folder = self.get_extracted_folder(source, self.version)

        if not os.path.isdir(extracted_folder):
            self._extract_tar(source, self.version)

        extracted_folder = self.get_extracted_folder(source, self.version)
        houdini_tar = os.path.join(extracted_folder, 'houdini.tar.gz')

        if not os.path.isfile(houdini_tar):
            raise EnvironmentError('Houdini tar file missing from "{extracted_folder}".'
                                   ''.format(extracted_folder=extracted_folder))

        self._extract_tar_file(houdini_tar, install)

        python_install_folder = os.path.join(install, 'python')

        for python_archive_file in self._get_python_tar_files(extracted_folder):
            self._extract_tar_file(python_archive_file, python_install_folder)


# class WindowsAdapter(BaseHoudiniAdapter):

#     '''An adapter for installing Houdini onto a Windows machine.'''

# #    name = 'nuke'
# #    _install_archive_name_template = 'Nuke{major}.{minor}v{patch}-win-x86-release-64.zip'

# #    @staticmethod
# #    def _get_base_command(executable, root):
# #        '''Make the command used to install Nuke, on Windows.

# #        Args:
# #            executable (str): The absolute path to the ".exe" installer file to run.
# #            root (str): The absolute directory to where the ".exe" will send files to.

# #        '''
# #        # Reference: https://learn.foundry.com/nuke/content/getting_started/installation/installing_nuke_win.html
# #        #
# #        # Note: The ".exe" file normally gives you a few window prompts to have
# #        #       to click through.  We add "/silent" to skip these prompts and
# #        #       go straight to installation. Use "/verysilent" to hide the
# #        #       install progress bar.
# #        #
# #        return '{executable} /dir="{root}" /silent'.format(
# #            executable=executable, root=root)

# #    @classmethod
# #    def _extract_zip_from_version(cls, source, version):
# #        '''Find the ZIP file for Nuke, based on the given version, and extract it.

# #        Args:
# #            source (str):
# #                The root folder which contains the ZIP file.
# #            version (str):
# #                Some Nuke version to get the ZIP file of.

# #        Raises:
# #            EnvironmentError: If the found ZIP file for `version` does not exist.

# #        '''
# #        path = cls.get_archive_path_from_version(source, version)

# #        if not os.path.isfile(path):
# #            raise EnvironmentError('Zip file "{path}" does not exist.'
# #                                   ''.format(path=path))

# #        _LOGGER.debug('Extracting zip file "%s" using version, "%s"', path, str(version))

# #        cls._extract_zip(path, os.path.dirname(path))

#     # @classmethod
#     # def get_install_file(cls, root, version):
#     #     install_file_template = cls.get_archive_path(
#     #         root,
#     #         'houdini-{version}-win64-vc*.exe'.format(version=version),
#     #     )

#     #     try:
#     #         return list(glob.glob(install_file_template))[0]
#     #     except IndexError:
#     #         return ''

#     def get_preinstalled_executables(self):
#         '''Get a list of possible pre-installed executable Nuke files.

#         Raises:
#             RuntimeError:
#                 If we can't get version information from the stored version then
#                 this function will fail. Normally though, assuming this adapter
#                 was built correctly, this shouldn't occur.

#         Returns:
#             str: The absolute path to a Nuke executable.

#         '''
#         return helper.get_preinstalled_windows_executables(self.version)

#     def install_from_local(self, source, install):
#         '''Search for a local Nuke install-executable and run it, if it exists.

#         Args:
#             source (str):
#                 The absolute path to the package folder where the Nuke executable
#                 would be found.
#             install (str):
#                 The absolute directory where `source` will be installed into.

#         Raises:
#             RuntimeError: If the installation failed for some reason.

#         '''
#         try:
#             executable = super(WindowsAdapter, self).install_from_local(source, install)
#         except EnvironmentError:
#             self._extract_zip_from_version(source, self.version)
#             executable = super(WindowsAdapter, self).install_from_local(source, install)

#         command = self._get_base_command(executable, install)

#         _, stderr = subprocess.Popen(
#             command, stderr=subprocess.PIPE, shell=True).communicate()

#         if stderr:
#             raise RuntimeError('The local install failed with this message "{stderr}".'
#                                ''.format(stderr=stderr))


def register(source_path, install_path, system, distribution, architecture):
    '''Add installation options to all of the Houdini adapter classes.

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
        # ('Windows', WindowsAdapter),
    )

    for system_, adapter in adapters:
        adapter.strategies = []

        # add_houdini_from_ftp_build = functools.partial(
        #     base_builder.add_from_internet_build,
        #     'houdini', system, distribution, architecture, source_path, install_path)
        add_houdini_local_filesystem_build = functools.partial(
            base_builder.add_local_filesystem_build, source_path, install_path)

        adapter.strategies.append(('local', add_houdini_local_filesystem_build))
        # TODO : Re-add this once SideFX gets back to me. Ticket ID "SESI #67857"
        # adapter.strategies.append(('internet', add_houdini_from_ftp_build))
        adapter.strategies.append(('link', base_builder.add_link_build))

        chooser.register_build_adapter(adapter, 'houdini_installation', system_)
