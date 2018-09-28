#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import subprocess
import platform
import zipfile
import abc
import os

# IMPORT THIRD-PARTY LIBRARIES
import six

# IMPORT LOCAL LIBRARIES
from . import strategy


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):

    '''An adapter for installing the package onto the user's system.

    Attributes:
        _known_metadata_files (tuple[str]):
            Filenames to ignore when checking if the user has already installed the package.

    '''

    platform = ''
    _known_metadata_files = ('build.rxt', '.bez.yaml', 'package.py')

    def __init__(self, architecture):
        '''Create the instance and do nothing else.'''
        super(BaseAdapter, self).__init__()
        self.architecture = architecture

    @classmethod
    @abc.abstractmethod
    def get_from_local(cls, source, root):
        executable = cls._get_install_file(source)

        if not os.path.isfile(executable):
            raise EnvironmentError(
                'install_file "{executable}" does not exist. '
                'Check its spelling and try again.'.format(executable=executable))

        if not os.path.isdir(root):
            os.makedirs(root)

        return executable

    @classmethod
    def exit_required(cls, targets, install_path):
        '''Check if the user does not want to install the package.

        Args:
            targets (tuple[str]):
                The user's args which were passed through command-line.
                Example: If they wrote "rez-build my package --install" then
                `targets` would be ["install"].
            install_path (str):
                The absolute path to where the package's contents will be installed.

        Returns:
            bool: If the user has already installed the package.

        '''
        # TODO : Remove this `return False` later
        return False

        if not os.path.isdir(install_path):
            is_installed = False
        else:
            is_installed = bool([item for item in os.listdir(install_path)
                                if item not in cls._known_metadata_files])

        user_did_not_request_an_install = 'install' not in targets
        return is_installed or user_did_not_request_an_install

    @staticmethod
    def execute():
        # TODO : Replace with logging messages
        strategies = strategy.get_strategies()

        errors = []
        for name, choice in strategies:
            try:
                choice()
            except Exception as err:
                errors.append('strategy "{name}" did not succeed.'.format(name=name))
                errors.append('Original error: "{err}".'.format(err=err))
            else:
                print('strategy "{name}" succeeded.'.format(name=name))
                return

        for message in errors:
            print(message)

        raise RuntimeError(
            'No strategy to install the package suceeded. The strategies were, '
            '"{strategies}".'.format(strategies=[name for name, _ in strategies]))


class LinuxAdapter(BaseAdapter):

    platform = 'Linux'

    def __init__(self, architecture):
        '''Create the instance and do nothing else.'''
        super(LinuxAdapter, self).__init__(architecture)

    def get_from_local(cls, source, root):
        executable = super(LinuxAdapter, cls).get_from_local(source, root)
        zip_file = zipfile.ZipFile(executable, 'r')

        try:
            zip_file.extractall(root)
        except Exception:
            return False
        finally:
            zip_file.close()

    @staticmethod
    def _get_install_file(root):
        return os.path.join(root, 'archive', 'Nuke11.2v3-linux-x86-release-64-installer')


class WindowsAdapter(BaseAdapter):

    platform = 'Windows'

    def __init__(self, architecture):
        '''Create the instance and do nothing else.'''
        super(WindowsAdapter, self).__init__(architecture)

    @staticmethod
    def _get_base_command(executable, root):
        '''str: The command used to install Nuke, on Windows.'''
        return '{executable} /dir="{root}" /silent'.format(executable=executable, root=root)

    @staticmethod
    def _get_install_file(root):
        return os.path.join(root, 'archive', 'Nuke11.2v3-win-x86-release-64.exe')

    @classmethod
    def get_from_local(cls, source, root):
        executable = super(WindowsAdapter, cls).get_from_local(source, root)
        base = cls._get_base_command(executable, root)
        command = '{base}'.format(base=base)

        _, stderr = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True).communicate()

        if stderr:
            raise RuntimeError('The local install failed with this message "{stderr}".'.format(stderr=stderr))


def get_adapter(system=platform.system(), architecture=platform.architecture()):
    options = {
        'Linux': LinuxAdapter,
        'Windows': WindowsAdapter,
    }

    try:
        adapter = options[system]
    except KeyError:
        raise NotImplementedError('system "{system}" is not supported.'.format(system=system))

    return adapter(architecture)
