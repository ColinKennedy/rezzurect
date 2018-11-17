#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Maya Rez package in Linux.'''

# IMPORT STANDARD LIBRARIES
import glob
import os

# IMPORT LOCAL LIBRARIES
from . import maya_installation_setting
from ...utils import config_helper
from . import helper


class LinuxMayaSettingAdapter(maya_installation_setting.CommonMayaSettingAdapter):

    '''An adapter which is used to set up common settings / aliases for Maya.'''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Maya files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Maya executable.

        '''
        return helper.get_preinstalled_linux_executables(self.version)

    def _get_python_site_packages_folder(self, root):
        '''str: Find the absolute path to the Python version that comes with Maya.'''
        # Note: Throw the path into a garbage environment variable so that we
        #       can expand "{root}" to its actual path
        #

        site_packages_folder = '{root}/lib/python*/site-packages'.format(root=root)

        return list(glob.glob(site_packages_folder))[0]

    def _find_first_preinstalled_executable(self):
        '''str: Find the first Maya executable that can be found on-disk.'''
        for path in self.get_preinstalled_executables():
            if os.path.isfile(path):
                return path

        return ''

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.

        Raises:
            EnvironmentError: If the Maya package is not correctly installed
                              and could not be "discovered" (by linkage).

        '''
        super(LinuxMayaSettingAdapter, self).execute()

        major = helper.get_version_parts(self.version)
        base = self.get_install_root()

        if os.path.isdir(base):
            root = os.path.join(base, 'usr', 'autodesk', 'maya{major}'.format(major=major))
        else:
            root = os.path.dirname(os.path.dirname(self._find_first_preinstalled_executable()))

        if not os.path.isdir(root):
            raise EnvironmentError('Directory: "{root}" could not be found.'.format(root=root))

        self.env.PATH.prepend(os.path.join(root, 'bin'))
        self.env.MAYA_VERSION.set(self.version)
        self.env.MAYA_MAJOR_VERSION.set(major)
        self.env.MAYA_LOCATION.set(root)
        self.env.LD_LIBRARY_PATH.append(os.path.join(root, 'lib'))
        self.env.PYTHONPATH.append(self._get_python_site_packages_folder(root))

        # TODO : Finish. Actually, do I actually even need this?
        # self.env.AUTODESK_ADLM_THINCLIENT_ENV.set('{root}/AdlmThinClientCustomEnv.xml')
        # self.env.MAYA_COLOR_MANAGEMENT_POLICY_FILE.set('{root}/MayaNoColorManagement.xml')
