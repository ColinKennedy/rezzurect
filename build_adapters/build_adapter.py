#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import platform
import os

# IMPORT LOCAL LIBRARIES
from . import strategy


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
    def get_base_command(executable, root):
        '''str: The command used to install Nuke, on Windows.'''
        return '{executable} /dir="{root}" /silent'.format(executable=executable, root=root)


class LinuxAdapter(BaseAdapter):

    platform = 'Linux'

    def __init__(self, architecture):
        '''Create the instance and do nothing else.'''
        super(LinuxAdapter, self).__init__(architecture)

    def execute(self):
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

    def get_from_local(cls, source, root):
        executable = cls.get_install_file(source)

        if not os.path.isfile(executable):
            raise EnvironmentError(
                'install_file "{executable}" does not exist. '
                'Check its spelling and try again.'.format(executable=executable))

        if not os.path.isdir(root):
            os.makedirs(root)

        base = cls.get_base_command(executable, root)
        command = 'sudo {base}'.format(base=base)
        process = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True)
        _, stderr = process.communicate()

        return bool(stderr)

    @staticmethod
    def get_install_file(root):
        return os.path.join(root, 'Nuke11.2v3-linux-x86-release-64-installer')


class WindowsAdapter(BaseAdapter):

    platform = 'Windows'

    def __init__(self):
        '''Create the instance and do nothing else.'''
        super(WindowsAdapter, self).__init__()

    @staticmethod
    def get_install_file(root):
        return os.path.join(root, 'Nuke11.2v3-win-x86-release-64.exe')

    # @classmethod
    # def execute(cls, executable, root):
    #     base = cls.get_base_command(executable, root)
    #     command = '{base}'.format(base=base)
    #     return subprocess.Popen(command, shell=True).communicate()


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
